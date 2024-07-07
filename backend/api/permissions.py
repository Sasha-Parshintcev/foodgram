from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение, которое проверяет,является ли текущий
    пользователь автором объекта или выполняется безопасный HTTP-метод.

    Это разрешение позволяет:
    - Разрешить доступ для безопасных HTTP-методов (GET, HEAD, OPTIONS)
    - Разрешить доступ, если текущий пользователь является автором объекта
    - Запретить доступ во всех остальных случаях
    """
    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли текущий пользователь разрешение
        на выполнение запрошенного действия.
        """
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
