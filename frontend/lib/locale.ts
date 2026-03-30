import { cookies } from "next/headers";

export type Locale = "pt" | "en";

// Traduções simples para as páginas sensíveis (login/perfil).
const messages: Record<Locale, Record<string, string>> = {
  pt: {
    brand: "Schoolar-S",
    loginTitle: "Iniciar sessão",
    loginSubtitle: "Use as credenciais institucionais para entrar. Nada mais é mostrado nesta página.",
    changeTitle: "Alterar palavra-passe",
    changeSubtitle: "Atualize a palavra-passe validando com as credenciais atuais.",
    username: "Nome de utilizador",
    password: "Palavra-passe",
    passwordCurrent: "Palavra-passe atual",
    passwordNew: "Nova palavra-passe",
    loginButton: "Entrar",
    changeButton: "Alterar e entrar",
    profileTitle: "Perfil do utilizador",
    profileSubtitle: "Atualize nome, foto e palavra-passe sem sair da sessão.",
    identity: "Identidade",
    dataPhoto: "Dados e foto",
    firstName: "Nome próprio",
    lastName: "Apelido",
    saveProfile: "Guardar perfil",
    security: "Segurança",
    changePassword: "Alterar palavra-passe",
    backToDashboard: "Voltar ao painel",
    substratoTitle: "Organização Substrato",
    substratoSubtitle:
      "Plataforma e consultoria em dados educacionais que estrutura ecossistemas escolares de ponta a ponta.",
    mission: "Missão",
    missionText:
      "Conectar escolas, gestores, professores e decisores com dados acionáveis, garantindo segurança, rastreabilidade e velocidade operacional.",
    whatWeDo: "O que fazemos",
    howWeWork: "Como trabalhamos",
    bulletSuite: "Desenvolvimento da suite Schoolar-S para gestão escolar integrada.",
    bulletIntegration: "Integração segura com backends existentes (auth, relatórios, finanças).",
    bulletAudit: "Auditoria e monitorização contínua de dados críticos.",
    bulletDash: "Dashboards operacionais com ênfase em leitura rápida e consistência.",
    bulletTenant: "Arquiteturas orientadas a tenant com isolamento lógico.",
    bulletSecurity: "Adoção de padrões de segurança (sessões, CSRF, RBAC).",
    bulletObservability: "Observabilidade integrada (health, readiness, auditoria).",
    bulletUX: "Interfaces multilíngues e acessíveis por design.",
    contact: "Contacto",
    contactText: "Para parcerias, suporte ou implementação, fale connosco em",
    backToPanel: "Voltar ao painel",
  },
  en: {
    brand: "Schoolar-S",
    loginTitle: "Sign in",
    loginSubtitle: "Use your institutional credentials to sign in. Only the login form is shown.",
    changeTitle: "Change password",
    changeSubtitle: "Update your password by validating with current credentials.",
    username: "Username",
    password: "Password",
    passwordCurrent: "Current password",
    passwordNew: "New password",
    loginButton: "Sign in",
    changeButton: "Change and sign in",
    profileTitle: "User profile",
    profileSubtitle: "Update name, photo and password without leaving the session.",
    identity: "Identity",
    dataPhoto: "Details & photo",
    firstName: "First name",
    lastName: "Last name",
    saveProfile: "Save profile",
    security: "Security",
    changePassword: "Change password",
    backToDashboard: "Back to dashboard",
    substratoTitle: "Substrato Organization",
    substratoSubtitle:
      "Platform and consulting in educational data that powers end-to-end school ecosystems.",
    mission: "Mission",
    missionText:
      "Connect schools, leaders, teachers, and decision-makers with actionable data, ensuring security, traceability, and operational speed.",
    whatWeDo: "What we do",
    howWeWork: "How we work",
    bulletSuite: "Development of the Schoolar-S suite for integrated school management.",
    bulletIntegration: "Secure integration with existing backends (auth, reports, finance).",
    bulletAudit: "Continuous auditing and monitoring of critical data.",
    bulletDash: "Operational dashboards focused on fast reading and consistency.",
    bulletTenant: "Tenant-oriented architectures with logical isolation.",
    bulletSecurity: "Security best practices (sessions, CSRF, RBAC).",
    bulletObservability: "Built-in observability (health, readiness, audit).",
    bulletUX: "Multilingual and accessible interfaces by design.",
    contact: "Contact",
    contactText: "For partnerships, support, or implementation, reach us at",
    backToPanel: "Back to dashboard",
  },
};

export async function getLocale(): Promise<Locale> {
  try {
    const cookieStore = await cookies();
    const fromCookie = (cookieStore.get("ui_locale")?.value || "").toLowerCase();
    return fromCookie === "en" ? "en" : "pt";
  } catch {
    return "pt";
  }
}

export function t(locale: Locale, key: string): string {
  return messages[locale]?.[key] || messages.pt[key] || key;
}
