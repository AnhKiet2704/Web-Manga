# Thêm vào manga/views.py hoặc tạo file mới manga/crud_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Manga, Chapter, ChapterImage, Category, Author
from django.core.files.storage import FileSystemStorage
import zipfile
import os


# Kiểm tra user có phải admin không
def is_admin(user):
    return user.is_staff or user.is_superuser


# ==================== MANGA CRUD ====================

@login_required
@user_passes_test(is_admin)
def manga_list(request):
    """Danh sách tất cả truyện"""
    mangas = Manga.objects.all().order_by('-created_at')
    return render(request, 'crud/manga_list.html', {'mangas': mangas})


@login_required
@user_passes_test(is_admin)
def manga_create(request):
    """Tạo truyện mới"""
    if request.method == 'POST':
        title = request.POST.get('title')
        alternative_title = request.POST.get('alternative_title', '')
        description = request.POST.get('description')
        author_id = request.POST.get('author')
        status = request.POST.get('status', 'ongoing')
        cover_image = request.FILES.get('cover_image')
        category_ids = request.POST.getlist('categories')

        # Tạo manga
        manga = Manga.objects.create(
            title=title,
            alternative_title=alternative_title,
            description=description,
            author_id=author_id,
            status=status,
            cover_image=cover_image
        )

        # Thêm thể loại
        manga.categories.set(category_ids)

        messages.success(request, f'Đã tạo truyện "{title}" thành công!')
        return redirect('crud_manga_list')

    # GET request - hiển thị form
    categories = Category.objects.all()
    authors = Author.objects.all()
    return render(request, 'crud/manga_form.html', {
        'categories': categories,
        'authors': authors,
        'action': 'create'
    })


@login_required
@user_passes_test(is_admin)
def manga_update(request, manga_id):
    """Cập nhật truyện"""
    manga = get_object_or_404(Manga, id=manga_id)

    if request.method == 'POST':
        manga.title = request.POST.get('title')
        manga.alternative_title = request.POST.get('alternative_title', '')
        manga.description = request.POST.get('description')
        manga.author_id = request.POST.get('author')
        manga.status = request.POST.get('status', 'ongoing')

        # Cập nhật ảnh bìa nếu có
        if 'cover_image' in request.FILES:
            manga.cover_image = request.FILES['cover_image']

        manga.save()

        # Cập nhật thể loại
        category_ids = request.POST.getlist('categories')
        manga.categories.set(category_ids)

        messages.success(request, f'Đã cập nhật truyện "{manga.title}" thành công!')
        return redirect('crud_manga_list')

    # GET request - hiển thị form với dữ liệu hiện tại
    categories = Category.objects.all()
    authors = Author.objects.all()
    return render(request, 'crud/manga_form.html', {
        'manga': manga,
        'categories': categories,
        'authors': authors,
        'action': 'update'
    })


@login_required
@user_passes_test(is_admin)
def manga_delete(request, manga_id):
    """Xóa truyện"""
    manga = get_object_or_404(Manga, id=manga_id)

    if request.method == 'POST':
        title = manga.title
        manga.delete()
        messages.success(request, f'Đã xóa truyện "{title}" thành công!')
        return redirect('crud_manga_list')

    return render(request, 'crud/manga_confirm_delete.html', {'manga': manga})


# ==================== CHAPTER CRUD ====================

@login_required
@user_passes_test(is_admin)
def chapter_list(request, manga_id):
    """Danh sách chapter của truyện"""
    manga = get_object_or_404(Manga, id=manga_id)
    chapters = manga.chapters.all().order_by('-chapter_number')
    return render(request, 'crud/chapter_list.html', {
        'manga': manga,
        'chapters': chapters
    })


@login_required
@user_passes_test(is_admin)
def chapter_create(request, manga_id):
    """Tạo chapter mới"""
    manga = get_object_or_404(Manga, id=manga_id)

    if request.method == 'POST':
        chapter_number = request.POST.get('chapter_number')
        title = request.POST.get('title', '')

        # Tạo chapter
        chapter = Chapter.objects.create(
            manga=manga,
            chapter_number=float(chapter_number),
            title=title
        )

        # Xử lý upload ảnh
        # 1. Upload từng ảnh
        images = request.FILES.getlist('images')
        for idx, image in enumerate(images, start=1):
            ChapterImage.objects.create(
                chapter=chapter,
                image=image,
                page_number=idx
            )

        # 2. Upload ZIP (nếu có)
        zip_file = request.FILES.get('zip_file')
        if zip_file:
            # Lưu ZIP tạm thời
            fs = FileSystemStorage()
            filename = fs.save(zip_file.name, zip_file)
            uploaded_file_path = fs.path(filename)

            # Giải nén và lưu ảnh
            with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
                image_files = sorted([f for f in zip_ref.namelist()
                                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))])

                for idx, img_name in enumerate(image_files, start=1):
                    img_data = zip_ref.read(img_name)

                    # Lưu ảnh vào ChapterImage
                    from django.core.files.base import ContentFile
                    chapter_image = ChapterImage(
                        chapter=chapter,
                        page_number=idx
                    )
                    chapter_image.image.save(
                        f"ch{chapter.chapter_number}_p{idx}.jpg",
                        ContentFile(img_data),
                        save=True
                    )

            # Xóa file ZIP tạm
            os.remove(uploaded_file_path)

        messages.success(request, f'Đã tạo Chapter {chapter_number} thành công!')
        return redirect('crud_chapter_list', manga_id=manga.id)

    return render(request, 'crud/chapter_form.html', {
        'manga': manga,
        'action': 'create'
    })


@login_required
@user_passes_test(is_admin)
def chapter_update(request, chapter_id):
    """Cập nhật chapter"""
    chapter = get_object_or_404(Chapter, id=chapter_id)

    if request.method == 'POST':
        chapter.chapter_number = float(request.POST.get('chapter_number'))
        chapter.title = request.POST.get('title', '')
        chapter.save()

        messages.success(request, f'Đã cập nhật Chapter {chapter.chapter_number} thành công!')
        return redirect('crud_chapter_list', manga_id=chapter.manga.id)

    return render(request, 'crud/chapter_form.html', {
        'chapter': chapter,
        'manga': chapter.manga,
        'action': 'update'
    })


@login_required
@user_passes_test(is_admin)
def chapter_delete(request, chapter_id):
    """Xóa chapter"""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    manga_id = chapter.manga.id

    if request.method == 'POST':
        chapter_num = chapter.chapter_number
        chapter.delete()
        messages.success(request, f'Đã xóa Chapter {chapter_num} thành công!')
        return redirect('crud_chapter_list', manga_id=manga_id)

    return render(request, 'crud/chapter_confirm_delete.html', {'chapter': chapter})


# ==================== CATEGORY CRUD ====================

@login_required
@user_passes_test(is_admin)
def category_list(request):
    """Danh sách thể loại"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'crud/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
def category_create(request):
    """Tạo thể loại mới"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        Category.objects.create(name=name, description=description)
        messages.success(request, f'Đã tạo thể loại "{name}" thành công!')
        return redirect('crud_category_list')

    return render(request, 'crud/category_form.html', {'action': 'create'})


@login_required
@user_passes_test(is_admin)
def category_update(request, category_id):
    """Cập nhật thể loại"""
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.save()

        messages.success(request, f'Đã cập nhật thể loại "{category.name}" thành công!')
        return redirect('crud_category_list')

    return render(request, 'crud/category_form.html', {
        'category': category,
        'action': 'update'
    })


@login_required
@user_passes_test(is_admin)
def category_delete(request, category_id):
    """Xóa thể loại"""
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Đã xóa thể loại "{name}" thành công!')
        return redirect('crud_category_list')

    return render(request, 'crud/category_confirm_delete.html', {'category': category})


# ==================== AUTHOR CRUD ====================

@login_required
@user_passes_test(is_admin)
def author_list(request):
    """Danh sách tác giả"""
    authors = Author.objects.all().order_by('name')
    return render(request, 'crud/author_list.html', {'authors': authors})


@login_required
@user_passes_test(is_admin)
def author_create(request):
    """Tạo tác giả mới"""
    if request.method == 'POST':
        name = request.POST.get('name')
        bio = request.POST.get('bio', '')

        Author.objects.create(name=name, bio=bio)
        messages.success(request, f'Đã tạo tác giả "{name}" thành công!')
        return redirect('crud_author_list')

    return render(request, 'crud/author_form.html', {'action': 'create'})


@login_required
@user_passes_test(is_admin)
def author_update(request, author_id):
    """Cập nhật tác giả"""
    author = get_object_or_404(Author, id=author_id)

    if request.method == 'POST':
        author.name = request.POST.get('name')
        author.bio = request.POST.get('bio', '')
        author.save()

        messages.success(request, f'Đã cập nhật tác giả "{author.name}" thành công!')
        return redirect('crud_author_list')

    return render(request, 'crud/author_form.html', {
        'author': author,
        'action': 'update'
    })


@login_required
@user_passes_test(is_admin)
def author_delete(request, author_id):
    """Xóa tác giả"""
    author = get_object_or_404(Author, id=author_id)

    if request.method == 'POST':
        name = author.name
        author.delete()
        messages.success(request, f'Đã xóa tác giả "{name}" thành công!')
        return redirect('crud_author_list')

    return render(request, 'crud/author_confirm_delete.html', {'author': author})