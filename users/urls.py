from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path(
        "register-student/",
        views.StudentRegisterView.as_view(),
        name="register-student",
    ),
    path(
        "verify/<str:token>/",
        views.AccountVerificationView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification-email/",
        views.ResendVerificationEmailView.as_view(),
        name="resend-verification-email",
    ),
    path(
        "request-password-reset/",
        views.RequestPasswordResetView.as_view(),
        name="request-password-reset",
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path(
        "student-login/",
        views.StudentLoginView.as_view(),
        name="student-login",
    ),
    path("register-tutor/", views.TutorRegisterView.as_view(), name="register-tutor"),
    path("all-users/", views.UserListView.as_view(), name="all-users"),
    path(
        "students/<int:pk>/",
        views.StudentUserDetailView.as_view(),
        name="student-detail",
    ),
    path(
        "tutors/<int:pk>/", views.StudentUserDetailView.as_view(), name="tutor-detail"
    ),
    path(
        "student-profile/",
        views.StudentProfileView.as_view(),
        name="student-profile",
    ),
    path(
        "student-profile/<int:pk>/",
        views.StudentUserProfile.as_view(),
        name="student-profile",
    ),
    path(
        "refresh-token/",
        views.RefreshTokenView.as_view(),
        name="refresh-token",
    ),
    path(
        "google-signin/",
        views.GoogleSignInView.as_view(),
        name="google-signin",
    ),
    path(
        "google-signin-callback/",
        views.GoogleSignInCallbackView.as_view(),
        name="google-signin-callback",
    ),
]
