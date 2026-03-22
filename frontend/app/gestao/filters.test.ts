import test from "node:test";
import assert from "node:assert/strict";

import type { GestaoSnapshot } from "@/lib/api";

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

function createCollection<T>(items: T[]) {
  return {
    ok: true,
    status: "ONLINE",
    statusCode: 200,
    count: items.length,
    items,
    message: `${items.length} registos carregados do backend.`,
    requiresAuth: false,
  };
}

function createSnapshot(): GestaoSnapshot {
  return {
    baseUrlLabel: "http://localhost:8000",
    authConfigured: false,
    tenantId: null,
    health: {
      ok: true,
      status: "ONLINE",
      message: "ok",
    },
    readiness: {
      ok: true,
      status: "OK",
      message: "ok",
    },
    anosLetivos: createCollection([
      {
        id: 1,
        codigo: "2025",
        data_inicio: "2025-01-01",
        data_fim: "2025-12-31",
        ativo: true,
      },
      {
        id: 2,
        codigo: "2026",
        data_inicio: "2026-01-01",
        data_fim: "2026-12-31",
        ativo: true,
      },
    ]),
    escolas: createCollection([
      {
        id: 1,
        codigo: "ESC-01",
        nome: "Escola Central",
        distrito: "A",
        provincia: "Maputo",
        ativa: true,
      },
      {
        id: 2,
        codigo: "ESC-02",
        nome: "Escola Norte",
        distrito: "B",
        provincia: "Gaza",
        ativa: true,
      },
    ]),
    turmas: createCollection([
      {
        id: 10,
        nome: "7A",
        escola: 1,
        escola_nome: "Escola Central",
        classe: 7,
        classe_nome: "7a Classe",
        ciclo: 2,
        ano_letivo: "2025",
        professor_responsavel: 90,
        professor_responsavel_nome: "Ana",
      },
      {
        id: 11,
        nome: "8B",
        escola: 2,
        escola_nome: "Escola Norte",
        classe: 8,
        classe_nome: "8a Classe",
        ciclo: 2,
        ano_letivo: "2026",
        professor_responsavel: 91,
        professor_responsavel_nome: "Beto",
      },
    ]),
    matriculas: createCollection([
      {
        id: 100,
        aluno: 1,
        aluno_nome: "Carla",
        turma: 10,
        turma_nome: "7A",
        data_matricula: "2025-01-03",
        escola_nome: "Escola Central",
        ano_letivo: "2025",
        classe: 7,
      },
      {
        id: 101,
        aluno: 2,
        aluno_nome: "Dino",
        turma: 11,
        turma_nome: "8B",
        data_matricula: "2026-01-03",
        escola_nome: "Escola Norte",
        ano_letivo: "2026",
        classe: 8,
      },
    ]),
    atribuicoesGestao: createCollection([
      {
        id: 1000,
        professor: 90,
        professor_nome: "Ana",
        escola: 1,
        escola_nome: "Escola Central",
        ano_letivo: 1,
        ano_letivo_codigo: "2025",
        cargo: "DIRECTOR_DE_TURMA",
        classe: 7,
        classe_numero: 7,
        turma: 10,
        turma_nome: "7A",
        ciclo: 2,
        ativo: true,
      },
      {
        id: 1001,
        professor: 91,
        professor_nome: "Beto",
        escola: 2,
        escola_nome: "Escola Norte",
        ano_letivo: 2,
        ano_letivo_codigo: "2026",
        cargo: "COORDENADOR_DE_CICLO",
        classe: null,
        classe_numero: undefined,
        turma: null,
        turma_nome: undefined,
        ciclo: 2,
        ativo: true,
      },
    ]),
  };
}

test("readParam normaliza strings e arrays", () => {
  assert.equal(readParam("abc"), "abc");
  assert.equal(readParam(["abc", "def"]), "abc");
  assert.equal(readParam(undefined), "");
});

test("formatCargo substitui underscores por espacos", () => {
  assert.equal(formatCargo("DIRECTOR_DE_TURMA"), "DIRECTOR DE TURMA");
});

test("filterTurmas aplica filtros por escola e ano", () => {
  const snapshot = createSnapshot();
  const result = filterTurmas(snapshot, {
    escola: "1",
    ano: "2025",
    cargo: "",
  });

  assert.deepEqual(
    result.map((item) => item.id),
    [10],
  );
});

test("filterMatriculas usa a turma para filtrar por escola", () => {
  const snapshot = createSnapshot();
  const result = filterMatriculas(snapshot, {
    escola: "2",
    ano: "",
    cargo: "",
  });

  assert.deepEqual(
    result.map((item) => item.id),
    [101],
  );
});

test("filterAtribuicoes combina escola, ano e cargo", () => {
  const snapshot = createSnapshot();
  const result = filterAtribuicoes(snapshot, {
    escola: "2",
    ano: "2026",
    cargo: "COORDENADOR_DE_CICLO",
  });

  assert.deepEqual(
    result.map((item) => item.id),
    [1001],
  );
});

test("helpers contam turmas e matriculas corretamente", () => {
  const snapshot = createSnapshot();

  assert.equal(countTurmasDaEscola(snapshot.turmas.items, 1), 1);
  assert.equal(countMatriculasDaTurma(snapshot.matriculas.items, 10), 1);
});

test("describeEscopoAtribuicao prioriza turma, depois classe e depois ciclo", () => {
  const snapshot = createSnapshot();

  assert.equal(describeEscopoAtribuicao(snapshot.atribuicoesGestao.items[0]), "7A");
  assert.equal(describeEscopoAtribuicao(snapshot.atribuicoesGestao.items[1]), "Ciclo 2");
});
