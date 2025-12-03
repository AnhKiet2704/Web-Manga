from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q, Count, Avg, Max
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import *


# ==================== TRANG CHỦ ====================
def home(request):
    # Truyện mới cập nhật
    latest_manga = Manga.objects.prefetch_related('chapters').order_by('-updated_at')[:20]

    # Top ngày/tuần/tháng
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    top_today = Manga.objects.filter(
        viewcount__date=today
    ).annotate(
        daily_views=Count('viewcount')
    ).order_by('-daily_views')[:10]

    top_week = Manga.objects.filter(
        viewcount__date__gte=week_ago
    ).annotate(
        weekly_views=Count('viewcount')
    ).order_by('-weekly_views')[:10]

    top_month = Manga.objects.filter(
        viewcount__date__gte=month_ago
    ).annotate(
        monthly_views=Count('viewcount')
    ).order_by('-monthly_views')[:10]

    # Tất cả thể loại
    categories = Category.objects.all()

    context = {
        'latest_manga': latest_manga,
        'top_today': top_today,
        'top_week': top_week,
        'top_month': top_month,
        'categories': categories,
    }
    return render(request, 'home.html', context)


# ==================== CHI TIẾT TRUYỆN ====================
def manga_detail(request, slug):
    manga = get_object_or_404(Manga, slug=slug)

    # Tăng lượt xem
    manga.views += 1
    manga.save(update_fields=['views'])

    # Cập nhật ViewCount theo ngày
    view_count, created = ViewCount.objects.get_or_create(
        manga=manga,
        date=timezone.now().date(),
        defaults={'count': 0}
    )
    view_count.count += 1
    view_count.save()

    # Lấy danh sách chapter
    chapters = manga.chapters.all().order_by('-chapter_number')

    # Kiểm tra user có follow không
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user=request.user, manga=manga).exists()

    # Lấy bình luận
    comments = manga.comments.filter(parent=None).select_related('user')[:10]

    # Tính rating trung bình
    avg_rating = manga.ratings.aggregate(Avg('score'))['score__avg'] or 0

    context = {
        'manga': manga,
        'chapters': chapters,
        'is_following': is_following,
        'comments': comments,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'manga_detail.html', context)


# ==================== TRANG ĐỌC TRUYỆN ====================
def read_chapter(request, manga_slug, chapter_slug):
    chapter = get_object_or_404(Chapter, slug=chapter_slug, manga__slug=manga_slug)

    # Tăng lượt xem chapter
    chapter.views += 1
    chapter.save(update_fields=['views'])

    # Lưu lịch sử đọc
    if request.user.is_authenticated:
        ReadingHistory.objects.update_or_create(
            user=request.user,
            chapter=chapter,
            defaults={'manga': chapter.manga}
        )

    # Lấy tất cả ảnh của chapter
    images = chapter.images.all().order_by('page_number')

    # Chapter trước/sau
    next_chapter = chapter.get_next_chapter()
    prev_chapter = chapter.get_previous_chapter()

    # Tất cả chapter của truyện
    all_chapters = chapter.manga.chapters.all().order_by('-chapter_number')

    context = {
        'chapter': chapter,
        'manga': chapter.manga,
        'images': images,
        'next_chapter': next_chapter,
        'prev_chapter': prev_chapter,
        'all_chapters': all_chapters,
    }
    return render(request, 'reader.html', context)


# ==================== TÌM KIẾM ====================
def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    mangas = Manga.objects.all()

    if query:
        mangas = mangas.filter(
            Q(title__icontains=query) |
            Q(alternative_title__icontains=query) |
            Q(author__name__icontains=query)
        )

    if category:
        mangas = mangas.filter(categories__slug=category)

    if status:
        mangas = mangas.filter(status=status)

    # Phân trang
    paginator = Paginator(mangas, 24)
    page = request.GET.get('page')
    mangas = paginator.get_page(page)

    categories = Category.objects.all()

    context = {
        'mangas': mangas,
        'query': query,
        'categories': categories,
        'selected_category': category,
        'selected_status': status,
    }
    return render(request, 'search.html', context)


# ==================== XEM THEO THỂ LOẠI ====================
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    mangas = category.mangas.all()

    paginator = Paginator(mangas, 24)
    page = request.GET.get('page')
    mangas = paginator.get_page(page)

    context = {
        'category': category,
        'mangas': mangas,
    }
    return render(request, 'category.html', context)


# ==================== ĐĂNG KÝ ====================
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Mật khẩu không khớp!')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user)

        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('login')

    return render(request, 'auth/register.html')


# ==================== ĐĂNG NHẬP ====================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')

    return render(request, 'auth/login.html')


# ==================== ĐĂNG XUẤT ====================
def logout_view(request):
    logout(request)
    return redirect('home')


# ==================== HỒ SƠ NGƯỜI DÙNG ====================
@login_required
def profile(request):
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        request.user.profile.bio = bio
        request.user.profile.save()
        messages.success(request, 'Cập nhật hồ sơ thành công!')
        return redirect('profile')

    return render(request, 'user/profile.html')


# ==================== LỊCH SỬ ĐỌC ====================
@login_required
def reading_history(request):
    history = ReadingHistory.objects.filter(user=request.user).select_related('manga', 'chapter')[:50]

    context = {
        'history': history,
    }
    return render(request, 'user/history.html', context)


# ==================== THEO DÕI TRUYỆN ====================
@login_required
def follow_manga(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)

    follow, created = Follow.objects.get_or_create(user=request.user, manga=manga)

    if not created:
        follow.delete()
        messages.success(request, f'Đã bỏ theo dõi {manga.title}')
    else:
        messages.success(request, f'Đã theo dõi {manga.title}')

    return redirect('manga_detail', slug=manga.slug)


# ==================== DANH SÁCH THEO DÕI ====================
@login_required
def following_list(request):
    follows = Follow.objects.filter(user=request.user).select_related('manga')

    context = {
        'follows': follows,
    }
    return render(request, 'user/following.html', context)


# ==================== BÌNH LUẬN ====================
@login_required
def add_comment(request, manga_id):
    if request.method == 'POST':
        manga = get_object_or_404(Manga, id=manga_id)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        comment = Comment.objects.create(
            user=request.user,
            manga=manga,
            content=content,
            parent_id=parent_id if parent_id else None
        )

        messages.success(request, 'Đã thêm bình luận!')
        return redirect('manga_detail', slug=manga.slug)

    return redirect('home')


# ==================== ĐÁNH GIÁ ====================
@login_required
def rate_manga(request, manga_id):
    if request.method == 'POST':
        manga = get_object_or_404(Manga, id=manga_id)
        score = int(request.POST.get('score'))

        if 1 <= score <= 10:
            Rating.objects.update_or_create(
                user=request.user,
                manga=manga,
                defaults={'score': score}
            )

            # Cập nhật rating trung bình
            avg = manga.ratings.aggregate(Avg('score'))['score__avg']
            manga.rating = avg if avg else 0
            manga.save(update_fields=['rating'])

            messages.success(request, 'Đã đánh giá truyện!')

        return redirect('manga_detail', slug=manga.slug)

    return redirect('home')
