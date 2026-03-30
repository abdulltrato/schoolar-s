from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel, tenant_id_from_user


# Modelo que representa o encarregado/guardião de um aluno.
class Guardian(BaseNamedCodeModel):
    # Prefixo usado na geração de códigos automáticos.
    CODE_PREFIX = "GRD"
    # Campos que herdam tenant de um usuário relacionado.
    TENANT_INHERIT_USER_FIELDS = ("user",)

    # Usuário vinculado ao encarregado (opcional).
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
    )
    # Telefone de contato.
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    # E-mail de contato.
    email = models.EmailField(blank=True, verbose_name="E-mail")
    # Grau de parentesco ou relação com o aluno.
    relationship = models.CharField(max_length=60, blank=True, verbose_name="Parentesco")
    # Flag indicando se o encarregado está ativo.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        # Obtém tenant do perfil de usuário vinculado.
        profile_tenant_id = tenant_id_from_user(self.user)
        # Se houver tenant no perfil, valida coerência.
        if profile_tenant_id:
            # Bloqueia se tenant informado diverge do perfil.
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "O tenant do encarregado deve coincidir com o tenant do perfil do usuário vinculado."})
            # Se tenant não foi setado, herda do perfil.
            if not self.tenant_id:
                self.tenant_id = profile_tenant_id
        # Garante que tenant esteja preenchido no final.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        # Executa validações antes de salvar.
        self.full_clean()
        # Persiste registro com lógica padrão.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Exibe o nome ao converter para string.
        return self.name

    class Meta:
        # Texto singular exibido no admin.
        verbose_name = "Encarregado"
        # Texto plural exibido no admin.
        verbose_name_plural = "Encarregados"
        # Ordenação padrão por nome.
        ordering = ["name"]
