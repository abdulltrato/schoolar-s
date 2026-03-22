import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import {
  type AtribuicaoGestao,
  type Escola,
  type Matricula,
  type Turma,
  getGestaoSnapshot,
} from "@/lib/api";
import {
  countMatriculasDaTurma,
  countTurmasDaEscola,
  describeEscopoAtribuicao,
  filterAtribuicoes,
  filterMatriculas,
  filterTurmas,
  formatCargo,
  readParam,
} from "./filters";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function GestaoPage({ searchParams }: PageProps) {
  const snapshot = await getGestaoSnapshot();
  const params = (await searchParams) || {};
  const filters = {
    escola: readParam(params.escola),
    ano: readParam(params.ano),
    cargo: readParam(params.cargo),
  };
  const turmas = filterTurmas(snapshot, filters);
  const matriculas = filterMatriculas(snapshot, filters);
  const atribuicoes = filterAtribuicoes(snapshot, filters);

  return (
    <DashboardShell
      title="Gestao escolar"
      description="Leitura institucional da escola: unidades escolares, turmas, matriculas e cargos de gestao pedagógica."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Resumo"
              title="Escopo atual"
              description="Referencias rapidas para a leitura operacional desta pagina."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Escolas</dt>
                <dd>{snapshot.escolas.count} unidades registadas.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Turmas</dt>
                <dd>{turmas.length} turmas no recorte atual.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Matriculas</dt>
                <dd>{matriculas.length} alunos associados aos filtros.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegacao secundaria da gestao" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secoes</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#escolas">Escolas e cargos</a></li>
              <li><a href="#turmas">Turmas e matriculas</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      <FilterBar
        fields={[
          {
            name: "escola",
            label: "Escola",
            value: filters.escola,
            options: snapshot.escolas.items.map((item) => ({
              value: String(item.id),
              label: item.nome,
            })),
          },
          {
            name: "ano",
            label: "Ano Letivo",
            value: filters.ano,
            options: snapshot.anosLetivos.items.map((item) => ({
              value: item.codigo,
              label: item.codigo,
            })),
          },
          {
            name: "cargo",
            label: "Cargo",
            value: filters.cargo,
            options: Array.from(new Set(snapshot.atribuicoesGestao.items.map((item) => item.cargo))).map((item) => ({
              value: item,
              label: formatCargo(item),
            })),
          },
        ]}
      />

      <section id="escolas" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Escolas"
          subtitle="Base institucional de operacao do sistema."
          snapshot={snapshot.escolas}
          rows={snapshot.escolas.items.slice(0, 6)}
          renderRow={(escola: Escola) => {
            const turmasDaEscola = countTurmasDaEscola(snapshot.turmas.items, escola.id);

            return (
              <div key={escola.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{escola.nome}</p>
                  <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                    {escola.ativa ? "ativa" : "inativa"}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {escola.codigo} | {escola.distrito || "distrito nao definido"} | {escola.provincia || "provincia nao definida"}
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">{turmasDaEscola} turmas ligadas a esta escola.</p>
              </div>
            );
          }}
        />

        <RecordList
          title="Cargos de gestao"
          subtitle="Direcao e coordenacao por ano letivo e nivel de escopo."
          snapshot={snapshot.atribuicoesGestao}
          rows={atribuicoes.slice(0, 8)}
          renderRow={(atribuicao: AtribuicaoGestao) => (
            <div key={atribuicao.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{atribuicao.professor_nome}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {atribuicao.ano_letivo_codigo}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {formatCargo(atribuicao.cargo)} em {atribuicao.escola_nome}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {describeEscopoAtribuicao(atribuicao)}
              </p>
            </div>
          )}
        />
      </section>

      <section id="turmas" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Turmas"
          subtitle="Turmas vinculadas a escola, classe, ano letivo e director de turma."
          snapshot={snapshot.turmas}
          rows={turmas.slice(0, 8)}
          renderRow={(turma: Turma) => {
            const totalMatriculas = countMatriculasDaTurma(snapshot.matriculas.items, turma.id);

            return (
              <div key={turma.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{turma.nome}</p>
                  <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                    {totalMatriculas} matriculas
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {turma.escola_nome} | {turma.ano_letivo} | {turma.classe_nome}
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">
                  Director de turma: {turma.professor_responsavel_nome || "nao atribuido"}
                </p>
              </div>
            );
          }}
        />

        <RecordList
          title="Matriculas"
          subtitle="Distribuicao dos alunos nas turmas da escola."
          snapshot={snapshot.matriculas}
          rows={matriculas.slice(0, 8)}
          renderRow={(matricula: Matricula) => (
            <div key={matricula.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{matricula.aluno_nome}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {matricula.ano_letivo}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {matricula.escola_nome} | {matricula.turma_nome}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Classe {matricula.classe}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
