/* Busca cursos e turmas no sistema (Supabase) e preenche a página.
   Sem conexão, o conteúdo fixo do HTML continua valendo. */
(function(){
  var C = window.SITE || {};
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function data(iso){ if(!iso) return 'A definir'; var p = String(iso).slice(0,10).split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function horas(n){ n = Number(n || 0); return n ? n.toLocaleString('pt-BR') + ' h/a' : '—'; }
  function validade(m){ m = Number(m || 0); if(!m) return '—'; return m % 12 === 0 ? (m / 12) + (m === 12 ? ' ano' : ' anos') : m + ' meses'; }
  function zap(msg){ var n = String(C.whatsapp || '').replace(/\D/g, ''); if(n.length <= 11) n = '55' + n; return 'https://wa.me/' + n + '?text=' + encodeURIComponent(msg); }

  function rpc(nome){
    var chave = 'site_' + nome;
    try { var c = JSON.parse(sessionStorage.getItem(chave) || 'null'); if(c && Date.now() - c.t < 600000) return Promise.resolve(c.d); } catch(e){}
    return fetch(C.supabaseUrl + '/rest/v1/rpc/' + nome, {
      method: 'POST',
      headers: { apikey: C.anonKey, Authorization: 'Bearer ' + C.anonKey, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_slug: C.slug })
    }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(d){ try { sessionStorage.setItem(chave, JSON.stringify({ t: Date.now(), d: d })); } catch(e){} return d; });
  }

  /* Turmas: <div data-turmas data-limite="3"> */
  var listas = document.querySelectorAll('[data-turmas]');
  if(listas.length){
    rpc('site_turmas').then(function(ts){
      ts = (ts || []).filter(function(t){ return t.sigla; });
      if(!ts.length) return;
      listas.forEach(function(el){
        var lim = Number(el.getAttribute('data-limite') || 0);
        var lista = lim ? ts.slice(0, lim) : ts;
        el.innerHTML = lista.map(function(t){
          var nome = t.nome || t.sigla;
          return '<article class="turma"><div class="turma-cab"><small>Turma ' + esc(t.codigo) + '</small><h3>' + esc(nome) + '</h3></div>' +
            '<div class="turma-corpo"><dl class="campos">' +
            '<div><dt>Início</dt><dd class="num">' + esc(data(t.inicio)) + '</dd></div>' +
            '<div><dt>Término</dt><dd class="num">' + esc(data(t.fim)) + '</dd></div>' +
            '<div><dt>Turno</dt><dd>' + esc(t.turno || 'A definir') + '</dd></div>' +
            '<div><dt>Vagas</dt><dd class="num">' + (t.vagas ? esc(t.vagas) : 'Consulte') + '</dd></div></dl>' +
            '<div class="acoes"><a class="btn btn-ouro" href="' + esc(C.portal) + '">Garantir minha vaga</a>' +
            '<a class="btn btn-zap" target="_blank" rel="noopener" href="' + esc(zap('Olá! Tenho interesse na turma ' + t.codigo + ' (' + nome + ').')) + '">Tirar dúvidas</a></div></div></article>';
        }).join('');
      });
    }).catch(function(){});
  }

  /* Cursos do sistema: <tbody data-cursos> */
  var cursosEl = document.querySelectorAll('[data-cursos]');
  if(cursosEl.length){
    rpc('site_cursos').then(function(cs){
      if(!cs || !cs.length) return;
      cursosEl.forEach(function(el){
        el.innerHTML = cs.map(function(c){
          return '<tr><td><span class="sig">' + esc(c.sigla) + '</span></td><td><b>' + esc(c.nome) + '</b></td><td class="num">' + esc(horas(c.carga)) + '</td><td>' + esc(validade(c.validade_meses)) + '</td></tr>';
        }).join('');
      });
    }).catch(function(){});
  }
})();
