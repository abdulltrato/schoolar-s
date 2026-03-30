from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from core.admin_utils import TenantAwareAdmin, resolve_request_tenant

# Importa modelos a serem registrados no admin.
from .models import Student, StudentCompetency


# Form personalizado para o modelo Student no admin.
class StudentAdminForm(forms.ModelForm):
    class Meta:
        # Modelo alvo.
        model = Student
        # Inclui todos os campos no form.
        fields = "__all__"

    def __init__(self, *args, request=None, **kwargs):
        # Guarda request para resolver tenant posteriormente.
        self.request = request
        # Inicializa a superclasse.
        super().__init__(*args, **kwargs)
        # O modelo tem dois campos de usuário; remove `user` do form de criação.
        self.fields.pop("user", None)

    def clean(self):
        # Executa validações padrão.
        cleaned_data = super().clean()
        # Tenta obter tenant já existente no instance.
        tenant_id = (getattr(self.instance, "tenant_id", "") or "").strip()
        # Se não houver tenant setado, tenta herdar do request.
        if not tenant_id:
            tenant_id = (resolve_request_tenant(self.request) or "").strip()
        # Preenche tenant tanto na instância quanto nos dados limpos.
        if tenant_id:
            self.instance.tenant_id = tenant_id
            cleaned_data["tenant_id"] = tenant_id
        # Retorna dados validados.
        return cleaned_data

    def add_error(self, field, error):
        # Redireciona erro de tenant para non-field se campo não está no form.
        if field == "tenant_id" and field not in self.fields:
            return super().add_error(None, error)
        # Caso contrário, usa lógica padrão.
        return super().add_error(field, error)

    def _update_errors(self, errors):
        # Guarda erros de tenant temporariamente.
        tenant_errors = []
        if hasattr(errors, "error_dict") and "tenant_id" in errors.error_dict and "tenant_id" not in self.fields:
            tenant_errors = list(errors.error_dict.pop("tenant_id"))

        # Processa erros padrão.
        super()._update_errors(errors)

        # Reinsere erros de tenant como non-field errors.
        for tenant_error in tenant_errors:
            super().add_error(None, tenant_error)

    def _resolve_tenant_id(self, cleaned_data):
        # Alias para compatibilidade retroativa.
        return (resolve_request_tenant(self.request) or "").strip()


# Registro do modelo Student no admin.
@admin.register(Student)
class AlunoAdmin(TenantAwareAdmin):
    # Usa o form customizado acima.
    form = StudentAdminForm
    # Colunas exibidas na lista.
    list_display = ("name", "grade", "education_level", "cycle", "education_path", "technical_level", "estado")
    # Filtros laterais disponíveis.
    list_filter = ("cycle", "estado", "grade", "education_path", "technical_level")
    # Campos pesquisáveis.
    search_fields = ("name",)
    # Campos somente leitura.
    readonly_fields = ("tenant_id", "education_level", "cycle")
    # Usa widget de seleção horizontal para M2M de cursos.
    filter_horizontal = ("courses",)
    # Organização dos campos na página de edição.
    fieldsets = (
        (
            "Dados do aluno",
            {
                "fields": (
                    "name",
                    "birth_date",
                    "grade",
                    "education_level",
                    "cycle",
                    "estado",
                    "courses",
                )
            },
        ),
        (
            "Trilho de ensino",
            {
                "fields": (
                    "education_path",
                    "technical_level",
                    "technical_course",
                )
            },
        ),
        (
            "Documentos obrigatórios",
            {
                "fields": (
                    ("identification_document", "identification_document_name"),
                    ("previous_certificate", "previous_certificate_name"),
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "tenant_id",
                    "code",
                    "usuario",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )

    @admin.display(description="Nível de Ensino")
    def education_level(self, obj):
        # Se não há aluno ou grade, retorna placeholder.
        if not obj or not obj.grade:
            return "-"
        # Caso contrário, devolve o nível capitalizado.
        return obj.education_level.title()


# Form admin para competências do aluno.
class StudentCompetencyAdminForm(forms.ModelForm):
    class Meta:
        # Modelo alvo.
        model = StudentCompetency
        # Inclui todos os campos.
        fields = "__all__"

    def __init__(self, *args, request=None, **kwargs):
        # Guarda request para resolver tenant.
        self.request = request
        # Inicializa superclasse.
        super().__init__(*args, **kwargs)
        # Obtém tenant do request.
        tenant_id = self._resolve_request_tenant()
        # Ajusta queryset do campo student para restringir ao tenant.
        student_field = self.fields.get("student")
        if student_field is not None and tenant_id:
            student_field.queryset = student_field.queryset.filter(tenant_id=tenant_id)

    def clean(self):
        # Executa validação padrão.
        cleaned_data = super().clean()
        # Obtém aluno informado (novo ou existente).
        student = cleaned_data.get("student") or getattr(self.instance, "student", None)
        # Extrai tenant do aluno.
        tenant_id = (getattr(student, "tenant_id", "") or "").strip()
        # Propaga tenant para instância e dados limpos.
        if tenant_id:
            self.instance.tenant_id = tenant_id
            cleaned_data["tenant_id"] = tenant_id
        # Retorna dados validados.
        return cleaned_data

    def _resolve_request_tenant(self):
        # Encapsula função utilitária para facilitar testes/mocks.
        return resolve_request_tenant(self.request)


# Registro do modelo StudentCompetency no admin.
@admin.register(StudentCompetency)
class StudentCompetencyAdmin(TenantAwareAdmin):
    # Form customizado.
    form = StudentCompetencyAdminForm
    # Colunas exibidas na listagem.
    list_display = ("student", "competency", "nivel", "tenant_name")
    # Campos somente leitura.
    readonly_fields = ("tenant_id",)
    # Campos exibidos no formulário.
    fields = ("student", "competency", "nivel", "tenant_id")

    def tenant_name(self, obj):
        # Importa aqui para evitar dependência circular.
        from apps.school.models import School

        # Busca nome da escola pelo tenant.
        name = School.objects.filter(tenant_id=obj.tenant_id).values_list("name", flat=True).first()
        # Retorna nome encontrado ou o próprio tenant_id.
        return name or obj.tenant_id

    # Configurações de exibição da coluna no admin.
    tenant_name.short_description = "Tenant"
    tenant_name.admin_order_field = "tenant_id"
