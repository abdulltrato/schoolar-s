import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import { MetricCard } from "@/components/metric-card";
import { SectionTitle } from "@/components/section-title";
import { StatusCard } from "@/components/status-card";
import { getHomeSnapshot, type CollectionSnapshot } from "@/lib/api";

function toneForCollection(snapshot: CollectionSnapshot<unknown>) {
  return snapshot.ok ? "success" : "warning";
}

function statusForCollection(snapshot: CollectionSnapshot<unknown>) {
  if (snapshot.requiresAuth) {
    return "AUTH";
  }

  return snapshot.ok ? "ONLINE" : "OFFLINE";
}

export default async function Home() {
  const snapshot = await getHomeSnapshot();
  const modules = [
    {
      href: "/management",
      title: "Management",
      description: "Schools, classrooms, teachers, and leadership roles.",
    },
    {
      href: "/curriculum",
      title: "Curriculum",
      description: "Subject offerings and curriculum plans.",
    },
    {
      href: "/assessment",
      title: "Assessment",
      description: "Periods, components, records, and weighted results.",
    },
  ];

  return (
    <DashboardShell
      title="Executive School Platform"
      description="A high-level view of school operations, curriculum structure, and assessment. Details now live in dedicated modules."
      aside={(
        <section className="rounded-[0.9rem] border border-ink/10 bg-ink p-2.5 text-sand shadow-card">
          <SectionTitle
            eyebrow="Modules"
            title="Domain Navigation"
            description="The interface is split by functional area to reduce noise and improve operational reading."
            inverse
          />
          <nav aria-label="Atalhos de modulos" className="mt-2 grid gap-2">
            {modules.map((module) => (
              <Link
                key={module.href}
                href={module.href}
                className="rounded-[0.8rem] border border-white/10 bg-white/5 px-2.5 py-2 transition hover:border-white/25 hover:bg-white/10"
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-sand sm:text-xs">
                  {module.title}
                </p>
                <p className="mt-1 text-xs leading-4 text-sand/78 sm:text-sm">
                  {module.description}
                </p>
              </Link>
            ))}
          </nav>
        </section>
      )}
    >
      <section className="grid gap-2 md:grid-cols-3 xl:grid-cols-6">
        <MetricCard
          label="Schools"
          value={String(snapshot.schools.count)}
          detail="Registered and active school units."
        />
        <MetricCard
          label="Management"
          value={String(snapshot.managementAssignments.count)}
          detail="Defined coordination and leadership roles."
        />
        <MetricCard
          label="Plans"
          value={String(snapshot.subjectPlans.count)}
          detail="Curriculum plans by subject and grade."
        />
        <MetricCard
          label="Periods"
          value={String(snapshot.periods.count)}
          detail="Configured assessment calendar."
        />
        <MetricCard
          label="Components"
          value={String(snapshot.components.count)}
          detail="ACS, ACP, tests, exams, and coursework."
        />
        <MetricCard
          label="Results"
          value={String(snapshot.periodResults.count)}
          detail="Weighted averages by subject."
        />
      </section>

      <section className="grid gap-2">
        <div className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-2.5 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Status"
            title="Platform Connectivity"
            description="A compact read of the core resources. Use the modules to inspect each domain in detail."
          />
          <div className="mt-2 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            <StatusCard
              title="Healthcheck"
              status={snapshot.health.status}
              tone={snapshot.health.ok ? "success" : "warning"}
              body={snapshot.health.message}
            />
            <StatusCard
              title="Readiness"
              status={snapshot.readiness.status}
              tone={snapshot.readiness.ok ? "success" : "warning"}
              body={snapshot.readiness.message}
            />
            <StatusCard
              title="Management API"
              status={statusForCollection(snapshot.managementAssignments)}
              tone={toneForCollection(snapshot.managementAssignments)}
              body={snapshot.managementAssignments.message}
            />
            <StatusCard
              title="Curriculum API"
              status={statusForCollection(snapshot.subjectPlans)}
              tone={toneForCollection(snapshot.subjectPlans)}
              body={snapshot.subjectPlans.message}
            />
            <StatusCard
              title="Assessment API"
              status={statusForCollection(snapshot.periodResults)}
              tone={toneForCollection(snapshot.periodResults)}
              body={snapshot.periodResults.message}
            />
          </div>
        </div>
      </section>
    </DashboardShell>
  );
}
