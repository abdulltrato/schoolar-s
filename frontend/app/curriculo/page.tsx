import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import {
  type DisciplinaClasse,
  type PlanoCurricularDisciplina,
  getCurriculoSnapshot,
} from "@/lib/api";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(
  value: string | string[] | undefined,
) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function CurriculoPage({ searchParams }: PageProps) {
  const snapshot = await getCurriculoSnapshot();
  const params = (await searchParams) || {};
  const ano = readParam(params.ano);
  const classe = readParam(params.classe);

  const oferta = snapshot.disciplinasClasse.items.filter((item) => {
    if (ano && item.ano_letivo !== ano) {
      return false;
    }
    if (classe && String(item.classe) !== classe) {
      return false;
    }
    return true;
  });

  const planos = snapshot.planosDisciplina.items.filter((item) => {
    if (ano && item.ano_letivo !== ano) {
      return false;
    }
    if (classe && String(item.classe) !== classe) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Curriculo"
      description="Oferta disciplinar por classe e ano letivo, com planos curriculares formais por disciplina."
    >
      <FilterBar
        fields={[
          {
            name: "ano",
            label: "Ano Letivo",
            value: ano,
            options: snapshot.anosLetivos.items.map((item) => ({
              value: item.codigo,
              label: item.codigo,
            })),
          },
          {
            name: "classe",
            label: "Classe",
            value: classe,
            options: snapshot.classes.items.map((item) => ({
              value: String(item.numero),
              label: item.nome,
            })),
          },
        ]}
      />

      <section className="grid gap-6 lg:grid-cols-2">
        <RecordList
          title="Oferta disciplinar"
          subtitle="Disciplinas configuradas por classe e ano letivo."
          snapshot={snapshot.disciplinasClasse}
          rows={oferta.slice(0, 8)}
          renderRow={(disciplina: DisciplinaClasse) => (
            <div key={disciplina.id} className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{disciplina.disciplina_nome}</p>
                <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ink/70">
                  {disciplina.ano_letivo}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">Classe {disciplina.classe}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                Carga horaria semanal: {disciplina.carga_horaria_semanal}
              </p>
            </div>
          )}
        />

        <RecordList
          title="Planos curriculares"
          subtitle="Objetivos, metodologia e critérios avaliativos por disciplina."
          snapshot={snapshot.planosDisciplina}
          rows={planos.slice(0, 8)}
          renderRow={(plano: PlanoCurricularDisciplina) => (
            <div key={plano.id} className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{plano.disciplina_nome}</p>
                <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ink/70">
                  {plano.ano_letivo}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                Classe {plano.classe} | {plano.competencias_previstas.length} competencias
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {plano.criterios_avaliacao || plano.metodologia || plano.objetivos || "Plano sem detalhe textual preenchido."}
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
