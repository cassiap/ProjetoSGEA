-- ===== Tipos de evento =====
INSERT INTO tipo_evento (nome, descricao, data_criacao, data_atualizacao)
VALUES 
  ('Palestra','Eventos curtos', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('Minicurso','Aulas práticas', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- ===== Dois eventos de exemplo (ajuste títulos/datas se quiser) =====
INSERT INTO evento (
  TIPO_id, titulo, descricao, data_inicio, data_fim, horario, local, vagas,
  organizador_id, criado_em, atualizado_em
)
SELECT 
  (SELECT id FROM tipo_evento WHERE nome='Palestra' LIMIT 1),
  'Introdução ao Django', 'Visão geral do framework', '2025-10-20', '2025-10-20',
  '19:00–20:30', 'Auditório A', 60,
  (SELECT id FROM auth_user WHERE username='admin' LIMIT 1),
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE EXISTS (SELECT 1 FROM auth_user WHERE username='admin')
  AND NOT EXISTS (SELECT 1 FROM evento WHERE titulo='Introdução ao Django');

INSERT INTO evento (
  TIPO_id, titulo, descricao, data_inicio, data_fim, horario, local, vagas,
  organizador_id, criado_em, atualizado_em
)
SELECT 
  (SELECT id FROM tipo_evento WHERE nome='Minicurso' LIMIT 1),
  'Python para Web com Django', 'Formulários, views e templates', '2025-10-22', '2025-10-23',
  '18:30–21:30', 'Lab 101', 25,
  (SELECT id FROM auth_user WHERE username='admin' LIMIT 1),
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE EXISTS (SELECT 1 FROM auth_user WHERE username='admin')
  AND NOT EXISTS (SELECT 1 FROM evento WHERE titulo='Python para Web com Django');

-- ===== Inscrições para o usuário "aluno" (se existir) =====
INSERT INTO inscricao (participante_id, evento_id, criado_em)
SELECT 
  (SELECT id FROM auth_user WHERE username='aluno' LIMIT 1),
  e.id,
  CURRENT_TIMESTAMP
FROM evento e
WHERE e.titulo IN ('Introdução ao Django','Python para Web com Django')
  AND EXISTS (SELECT 1 FROM auth_user WHERE username='aluno')
  AND NOT EXISTS (
    SELECT 1 FROM inscricao i 
    WHERE i.participante_id = (SELECT id FROM auth_user WHERE username='aluno' LIMIT 1)
      AND i.evento_id = e.id
  );

-- ===== Emite 1 certificado para a primeira inscrição do "aluno" (se houver) =====
INSERT INTO certificado (inscricao_id, emitido_em, codigo_validacao)
SELECT i.id, CURRENT_TIMESTAMP, 'VAL-' || HEX(RANDOMBLOB(6))
FROM inscricao i
JOIN auth_user u ON u.id = i.participante_id
WHERE u.username = 'aluno'
  AND NOT EXISTS (SELECT 1 FROM certificado c WHERE c.inscricao_id = i.id)
ORDER BY i.id
LIMIT 1;
