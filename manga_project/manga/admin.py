from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import *
import zipfile
from django.core.files import File
from PIL import Image
import io


# ==================== INLINE ADMINS ====================
class ChapterImageInline(admin.TabularInline):
    model = ChapterImage
    extra = 1
    fields = ('page_number', 'image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "No image"


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ('chapter_number', 'title', 'views', 'created_at')
    readonly_fields = ('views', 'created_at')


# ==================== CATEGORY ADMIN ====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'manga_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def manga_count(self, obj):
        return obj.mangas.count()

    manga_count.short_description = 'Số truyện'


# ==================== AUTHOR ADMIN ====================
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'manga_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def manga_count(self, obj):
        return obj.manga_set.count()

    manga_count.short_description = 'Số truyện'


# ==================== MANGA ADMIN ====================
@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'views', 'rating', 'chapter_count', 'updated_at', 'cover_preview')
    list_filter = ('status', 'categories', 'created_at')
    search_fields = ('title', 'alternative_title', 'author__name')
    filter_horizontal = ('categories',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    inlines = [ChapterInline]

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'slug', 'alternative_title', 'author')
        }),
        ('Nội dung', {
            'fields': ('description', 'cover_image', 'status')
        }),
        ('Phân loại', {
            'fields': ('categories',)
        }),
        ('Thống kê', {
            'fields': ('views', 'rating'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('views', 'rating')

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.cover_image.url)
        return "No cover"

    cover_preview.short_description = 'Ảnh bìa'

    def chapter_count(self, obj):
        return obj.chapters.count()

    chapter_count.short_description = 'Số chapter'


# ==================== CHAPTER ADMIN ====================
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('manga', 'chapter_number', 'title', 'views', 'image_count', 'created_at')
    list_filter = ('manga', 'created_at')
    search_fields = ('manga__title', 'title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ChapterImageInline]

    fieldsets = (
        ('Thông tin', {
            'fields': ('manga', 'chapter_number', 'title', 'slug')
        }),
        ('Upload ảnh ZIP', {
            'fields': ('upload_zip',),
            'description': 'Upload file ZIP chứa ảnh chapter. Ảnh sẽ tự động được giải nén và thêm vào.'
        }),
        ('Thống kê', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('views',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Thêm field upload ZIP
        from django import forms
        form.base_fields['upload_zip'] = forms.FileField(required=False, help_text='Upload file ZIP chứa ảnh')
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Xử lý upload ZIP
        if 'upload_zip' in request.FILES:
            zip_file = request.FILES['upload_zip']

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Lấy danh sách file ảnh
                image_files = sorted([f for f in zip_ref.namelist()
                                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])

                for idx, img_name in enumerate(image_files, start=1):
                    # Đọc ảnh từ ZIP
                    img_data = zip_ref.read(img_name)

                    # Tạo ChapterImage
                    chapter_image = ChapterImage(
                        chapter=obj,
                        page_number=idx
                    )

                    # Lưu ảnh
                    chapter_image.image.save(
                        f"chapter_{obj.id}_page_{idx}.jpg",
                        File(io.BytesIO(img_data)),
                        save=True
                    )

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = 'Số trang'


# ==================== USER PROFILE ADMIN ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'avatar_preview')
    search_fields = ('user__username', 'user__email')

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 50%;"/>', obj.avatar.url)
        return "No avatar"

    avatar_preview.short_description = 'Avatar'


# ==================== FOLLOW ADMIN ====================
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'manga__title')
    date_hierarchy = 'created_at'


# ==================== READING HISTORY ADMIN ====================
@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'chapter', 'last_read_at')
    list_filter = ('last_read_at',)
    search_fields = ('user__username', 'manga__title')
    date_hierarchy = 'last_read_at'


# ==================== COMMENT ADMIN ====================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'manga__title', 'content')
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Nội dung'


# ==================== RATING ADMIN ====================
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'manga__title')


# ==================== VIEW COUNT ADMIN ====================
@admin.register(ViewCount)
class ViewCountAdmin(admin.ModelAdmin):
    list_display = ('manga', 'date', 'count')
    list_filter = ('date',)
    search_fields = ('manga__title',)
    date_hierarchy = 'date'


# Tùy chỉnh Admin site
admin.site.site_header = "Manga Website Admin"
admin.site.site_title = "Manga Admin"
admin.site.index_title = "Quản trị Website Đọc Truyện"