# 📘 SUBSTRATO EDUCAÇÃO (Schoolar-S)

## 🧠 Visão Geral

O **SUBSTRATO EDUCAÇÃO** é um módulo do ecossistema SUBSTRATO responsável por gerir, monitorar e evoluir o ensino básico com base em competências.

O sistema traduz o **Plano Curricular do Ensino Primário (PCEP)** numa infraestrutura digital escalável, preparada para operar desde uma school local até nível nacional.

---

## 🎯 Objetivo

Digitalizar e operacionalizar o ensino básico com base em:

* Ensino baseado em competências
* Avaliação contínua
* Progressão por ciclos
* Currículo nacional + local
* Monitoria educacional
* Integração governamental
* Operação offline-first
* Escalabilidade massiva (milhões de alunos)

---

## 🧱 Princípios de Arquitetura

* Domain-Driven Design (DDD)
* Event-Driven Architecture
* Multi-Tenant (por school)
* API-first
* Modular e desacoplado
* Offline-first
* Observabilidade completa
* Segurança robusta

---

## 🌍 Escalabilidade

| Nível     | Escala            |
| --------- | ----------------- |
| School    | 1k – 20k alunos   |
| Distrito  | 10 – 50 escolas   |
| Província | 100 – 500 escolas |
| Nacional  | milhões           |

---

# 🏫 MODELO EDUCACIONAL (BASE PCEP)

## 🎓 Estrutura do Ensino

* Ensino Basico
* 1º Ciclo → 1ª a 3ª grade
* 2º Ciclo → 4ª a 6ª grade

* Ensino Medio

* 1º Ciclo → 7ª a 9ª grade
* 2º Ciclo → 10ª a 11ª grade

Progressão:

* Automática dentro do cycle
* Avaliação no fim do cycle
* Retenção apenas em casos excepcionais

---

## 🧠 Modelo de Competências (CORE)

O sistema é orientado por competências organizadas em 7 áreas:

1. Linguagem e Comunicação
2. Saber Científico e Tecnológico
3. Raciocínio e Resolução de Problemas
4. Desenvolvimento Pessoal e Autonomia
5. Relacionamento Interpessoal
6. Bem-estar, Saúde e Ambiente
7. Sensibilidade Estética e Artística

👉 Competência é a unidade principal do sistema (não a score).

---

## 📚 Estrutura Curricular

### Áreas

* Comunicação e Ciências Sociais
* Ciências Naturais e Matemática
* Atividades Práticas e Tecnológicas

---

## 🌍 Currículo Local (20%)

O sistema suporta personalização curricular:

* Base nacional
* Extensão local (school/district/província)

Implementação:

* `curriculo_base`
* `curriculo_local`

---

## 🌐 Modalidades de Ensino

* Monolingue (Português)
* Bilingue (Língua local + Português)

Suporte:

* Conteúdo por idioma
* Avaliação por idioma
* Transição linguística progressiva

---

## 🧪 Sistema de Avaliação

Tipos:

* Diagnóstica
* Formativa
* Sumativa

Avalia:

* Conhecimentos
* Habilidades
* Atitudes

---

## 🎓 Perfil do Graduado

O sistema mede desenvolvimento em:

* Pessoal
* Sociocultural
* Técnico-científico

Usado para:

* Analytics
* Relatórios
* IA futura

---

# 🧠 MODELO DE DOMÍNIO (DDD)

## 📦 Bounded Contexts

* Academico
* Curriculo
* Assessment
* Progresso
* School
* Relatorios

---

## 👨‍🎓 Student

* Grade
* Ciclo
* Competências
* Avaliações
* Estado

---

## 🏫 School (Tenant)

* Isolamento por `tenant_id`
* Operação offline
* Gestão completa

---

## 📚 Currículo

* Base + Local
* Disciplinas
* Competências

---

## 🧪 Avaliação

* Associada a competências
* Contínua
* Multiformato

---

## 🔁 Progressão

* Baseada em competências
* Decisão formal no fim do cycle

---

## 📊 Relatórios

* Student
* School
* Nacional

---

# ⚡ ARQUITETURA DE EVENTOS

Eventos principais:

* aluno_registrado
* avaliacao_registrada
* competencia_atualizada
* ciclo_concluido
* relatorio_gerado

---

# 🌐 MULTI-TENANT

* School = tenant
* Isolamento lógico
* Preparado para shard por região

---

# 📡 OFFLINE-FIRST

Fluxo:

School (offline) → armazenamento local → sincronização → servidor central

---

# 📊 OBSERVABILIDADE

Métricas:

* Taxa de aprovação
* Retenção
* Evolução por competência

---

# 🔐 SEGURANÇA

RBAC:

* Teacher
* Diretor
* Admin
* Governo

Proteções:

* Criptografia
* Auditoria
* Isolamento por tenant

---

# 🧱 ESTRUTURA DO PROJETO

```
schoolar-s/
├── apps/
│   ├── academic/
│   ├── curriculum/
│   ├── assessment/
│   ├── progress/
│   ├── school/
│   ├── reports/
│   ├── events/
│   └── tenants/
├── application/
├── services/
├── core/
└── schoolar_s/
    └── settings/
```

---

# 🔌 INTEGRAÇÕES

* Sistemas governamentais
* Mobile apps
* Dashboards

---

# 🚀 ROADMAP

### Fase 1

* Gestão de alunos
* Avaliação básica
* Progressão

### Fase 2

* Relatórios avançados
* Monitoria

### Fase 3

* IA educacional

### Fase 4

* Integração nacional

---

# ⚙️ STACK TECNOLÓGICA

### Principais Tecnologias

- **Backend atual**: Django + DRF
- **Banco de dados atual**: SQLite para desenvolvimento
- **Cache atual**: cache local em memória
- **Testes atuais**: Django Test Runner
- **Direção futura**: PostgreSQL, Redis, events assíncronos, frontend dedicado e observabilidade

### Tecnologias Futuras

- Integração: REST + gRPC
- Mobile: React Native
- Cloud: AWS
- Infraestrutura como código: Terraform
- Orquestração de workflows: Airflow
- Data Warehouse: Redshift
- Data Lake: S3
- Machine Learning: Scikit-learn + TensorFlow
- CI/CD para ML: MLflow
- Feature Flags: LaunchDarkly
- A/B Testing: Optimizely
- ChatOps: Slack + custom bots
- Documentação de API: Swagger + Postman
- Gerenciamento de projetos: Jira + Confluence
- Comunicação: Slack + Microsoft Teams
- Versionamento: Git + GitHub
- Code Review: GitHub Pull Requests
- Automação de testes: Selenium + Cypress
- Monitoramento de performance: New Relic
- Gerenciamento de dependências: Poetry
- Gerenciamento de pacotes: PyPI
- Gerenciamento de segredos: HashiCorp Vault
- Gerenciamento de logs: ELK Stack
- Gerenciamento de configuração: Ansible
- Gerenciamento de incidentes: PagerDuty
- Gerenciamento de mudanças: Change Management
- Gerenciamento de capacidade: Capacity Planning
- Gerenciamento de custos: Cost Management
- Gerenciamento de riscos: Risk Management
- Gerenciamento de conformidade: Compliance Management
- Gerenciamento de qualidade: Quality Management
- Gerenciamento de fornecedores: Vendor Management
- Gerenciamento de contratos: Contract Management
- Gerenciamento de ativos: Asset Management
- Gerenciamento de identidade: Identity Management
- Gerenciamento de acesso: Access Management

---

# 🚀 INSTALAÇÃO

```shell script
git clone repo
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

Configuração atual:

* `DJANGO_SETTINGS_MODULE=schoolar_s.settings`
* Estrutura modular em `apps/`, `application/`, `core/`, `services/` e `schoolar_s/settings/`
* Endpoints operacionais de plataforma: `/health/` e `/ready/`
* Banco relacional com suporte a PostgreSQL via variáveis `POSTGRES_*`

Frontend:

```shell script
cd frontend
npm install
npm run dev
```

Variáveis do frontend:

* `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
* `API_BASE_URL=http://backend:8000`

Containers:

```shell script
docker compose -f infra/docker-compose.yml up --build
```

Esse compose sobe:

* `db` com PostgreSQL 16
* `backend` Django em `http://localhost:8000`
* `frontend` Next.js em `http://localhost:3000`

Atalho para abrir o `psql` no banco do compose:

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/psql.ps1
```

Scripts rapidos:

```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/docker-up.ps1
powershell -ExecutionPolicy Bypass -File infra/scripts/backup.ps1
powershell -ExecutionPolicy Bypass -File infra/scripts/reset.ps1
```

Kubernetes:

```shell script
kubectl apply -f infra/k8s/
```

---

# 📈 STATUS

* Fase: MVP backend em evolução
* APIs básicas operacionais por domínio
* Validações centrais e testes automatizados iniciais adicionados
* Base robusta adicionada: request tracing, readiness, throttle, escopo por tenant via header e contrato padronizado de erros
* Estrutura reorganizada em `apps`, `application`, `core`, `services` e `schoolar_s/settings`
* Migrations sincronizadas com os modelos atuais

---

# 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

1. Fork o projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`).
4. Push para a branch (`git push origin feature/nova-feature`).
5. Abra um Pull Request.

Para questões ou sugestões, abra uma issue no [GitHub](https://github.com/seu-usuario/schoolar-s/issues).

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📈 Status do Projeto

- **Fase Atual**: Desenvolvimento inicial (Fase 1 em andamento).
- **Última Atualização**: Março 2026.
- **Próximos Passos**: Implementação de avaliação básica e relatórios.

Para feedback ou ideias, entre em contato via [issues](https://github.com/seu-usuario/schoolar-s/issues).

---

# 🧠 CONCLUSÃO

Este sistema não é apenas software — é uma **infraestrutura digital educacional alinhada ao modelo oficial**, pronta para suportar crescimento, integração governamental e evolução com inteligência artificial.
