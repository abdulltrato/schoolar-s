import type {
  AtribuicaoGestao,
  GestaoSnapshot,
  Matricula,
  Turma,
} from "@/lib/api";

export type GestaoFilters = {
  escola: string;
  ano: string;
  cargo: string;
};

export function formatCargo(cargo: string) {
  return cargo.replaceAll("_", " ");
}

export function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export function filterTurmas(snapshot: GestaoSnapshot, filters: GestaoFilters) {
  return snapshot.turmas.items.filter((item) => {
    if (filters.escola && String(item.escola) !== filters.escola) {
      return false;
    }

    if (filters.ano && item.ano_letivo !== filters.ano) {
      return false;
    }

    return true;
  });
}

export function filterMatriculas(snapshot: GestaoSnapshot, filters: GestaoFilters) {
  return snapshot.matriculas.items.filter((item) => {
    if (
      filters.escola &&
      !snapshot.turmas.items.find(
        (turma) => turma.id === item.turma && String(turma.escola) === filters.escola,
      )
    ) {
      return false;
    }

    if (filters.ano && item.ano_letivo !== filters.ano) {
      return false;
    }

    return true;
  });
}

export function filterAtribuicoes(snapshot: GestaoSnapshot, filters: GestaoFilters) {
  return snapshot.atribuicoesGestao.items.filter((item) => {
    if (filters.escola && String(item.escola) !== filters.escola) {
      return false;
    }

    if (filters.ano && item.ano_letivo_codigo !== filters.ano) {
      return false;
    }

    if (filters.cargo && item.cargo !== filters.cargo) {
      return false;
    }

    return true;
  });
}

export function countTurmasDaEscola(turmas: Turma[], escolaId: number) {
  return turmas.filter((turma) => turma.escola === escolaId).length;
}

export function countMatriculasDaTurma(matriculas: Matricula[], turmaId: number) {
  return matriculas.filter((matricula) => matricula.turma === turmaId).length;
}

export function describeEscopoAtribuicao(atribuicao: AtribuicaoGestao) {
  return (
    atribuicao.turma_nome ||
    (atribuicao.classe_numero ? `Classe ${atribuicao.classe_numero}` : null) ||
    (atribuicao.ciclo ? `Ciclo ${atribuicao.ciclo}` : "Escopo da escola")
  );
}
