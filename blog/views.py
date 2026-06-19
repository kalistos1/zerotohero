

from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import BlogCategory, Comment, Post


# ── Shared base queryset ───────────────────────────────────────────────────────
#
# Never instantiate a raw queryset in the view body — always go through this
# function so every caller gets the same filters and index hints.

def _published_posts():
    """Return a base queryset of published posts only."""
    return (
        Post.objects
        .filter(status="PUBLISHED")
        .select_related("author", "category")
    )


# ── List view ──────────────────────────────────────────────────────────────────

def blog_list(request):
    qs = (
        _published_posts()
        .order_by("-date_created")
    )

    # Category filter via ?category=<slug>
    category_slug = request.GET.get("category", "").strip()
    active_category = None
    if category_slug:
        # Single extra query to validate slug before filtering (avoids silent empty page)
        try:
            active_category = BlogCategory.objects.only("id", "name", "slug").get(slug=category_slug)
            qs = qs.filter(category=active_category)
        except BlogCategory.DoesNotExist:
            qs = qs.none()  # invalid slug → empty page, not a 500

    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Fetch categories in one query; only the fields the sidebar needs
    categories = BlogCategory.objects.only("name", "slug").order_by("name")

    return render(request, "blog/blog_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "active_category": active_category,
        "category_slug": category_slug,
    })


# ── Detail view ────────────────────────────────────────────────────────────────

def blog_detail(request, slug):
    # prefetch_related on comments with nested author select_related:
    # results in exactly 3 queries: post, comments+authors, tags
    comments_qs = (
        Comment.objects
        .select_related("author")
        .only("text", "date_created", "author__username",
              "author__first_name", "author__last_name")
        .order_by("date_created")
    )

    post = get_object_or_404(
        Post.objects
        .filter(status="PUBLISHED")
        .select_related("author", "category")
        .prefetch_related(
            Prefetch("comments", queryset=comments_qs),
            "tags",
        ),
        slug=slug,
    )

    # Related posts: same category, published, most recent 3
    # .only() avoids loading body + images we won't display
    related_qs = (
        _published_posts()
        .filter(category=post.category)
        .exclude(pk=post.pk)
        .only("title", "slug", "date_created",
               "thumbnail", "image", "category__name")
        .order_by("-date_created")[:3]
    ) if post.category_id else Post.objects.none()

    return render(request, "blog/blog_detail.html", {
        "post": post,
        "related": related_qs,
        "comments": post.comments.all(),  # already prefetched — no extra query
    })
