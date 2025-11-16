// Fetch historia.json and render sections into the page
async function loadHistoria() {
  try {
    const res = await fetch('historia.json');
    if (!res.ok) throw new Error('No se puede cargar historia.json');
    const data = await res.json();

    // Title page: support two JSON schemas
    if (data.title_page) {
      const title = data.title_page || {};
      document.getElementById('story-main-title').textContent = title.title || 'Sin título';
      document.getElementById('story-subtitle').textContent = title.subtitle || '';
      document.getElementById('story-author').textContent = `${title.author || ''} — ${title.institution || ''}`;
    } else if (data.event) {
      // New short schema
      document.getElementById('story-main-title').textContent = data.event || 'Evento';
      document.getElementById('story-subtitle').textContent = data.date || '';
      const authorEl = document.getElementById('story-author');
      if (data.protagonist && data.protagonist.name) {
        authorEl.textContent = `${data.protagonist.name} — ${data.protagonist.action || ''}`;
      } else {
        authorEl.textContent = '';
      }
    }

    // Content
    const main = document.getElementById('story-content');
    main.innerHTML = '';
  for (const block of data.body || []) {
      if (block.type === 'section') {
        const sec = document.createElement('section');
        sec.className = 'story-section';
        const h2 = document.createElement('h2');
        h2.textContent = block.heading || '';
        sec.appendChild(h2);

        (block.content || []).forEach(pText => {
          const p = document.createElement('p');
          p.textContent = pText;
          sec.appendChild(p);
        });

        // Figures if present
        (block.figures || []).forEach(fig => {
          const figCap = document.createElement('div');
          figCap.className = 'story-figure';
          figCap.textContent = `${fig.id || ''} — ${fig.caption || ''}`;
          sec.appendChild(figCap);
        });

        // Subsections
        (block.subsections || []).forEach(sub => {
          const subh = document.createElement('h3');
          subh.textContent = sub.heading || '';
          sec.appendChild(subh);
          (sub.content || []).forEach(text => {
            const sp = document.createElement('p');
            sp.textContent = text;
            sec.appendChild(sp);
          });
          (sub.figures || []).forEach(fig => {
            const figCap = document.createElement('div');
            figCap.className = 'story-figure';
            figCap.textContent = `${fig.id || ''} — ${fig.caption || ''}`;
            sec.appendChild(figCap);
          });
        });

        main.appendChild(sec);
      }
    }

    // Footer / References
    const footer = document.getElementById('story-footer');
  if (data.references) {
      const h = document.createElement('h4');
      h.textContent = data.references.heading || 'Referencias';
      footer.appendChild(h);
      const ul = document.createElement('ul');
      for (const ref of data.references.items || []) {
        const li = document.createElement('li');
        li.textContent = ref;
        ul.appendChild(li);
      }
      footer.appendChild(ul);
    }
    // New schema: render summary and protagonist/outcome
    if (data.event) {
      // Render main summary as first section
      const summarySection = document.createElement('section');
      summarySection.className = 'story-section';
      const summaryH = document.createElement('h2');
      summaryH.textContent = 'Summary';
      summarySection.appendChild(summaryH);
      if (data.summary) {
        const p = document.createElement('p');
        p.textContent = data.summary;
        summarySection.appendChild(p);
      }
      // Protagonist
      if (data.protagonist) {
        const pro = document.createElement('section');
        pro.className = 'story-section';
        const ph = document.createElement('h2');
        ph.textContent = 'Protagonist';
        pro.appendChild(ph);
        ['name','action','narrative'].forEach(k => {
          if (data.protagonist[k]) {
            const p = document.createElement('p');
            p.textContent = data.protagonist[k];
            pro.appendChild(p);
          }
        });
        main.appendChild(pro);
      }
      // Outcome
      if (data.outcome) {
        const oc = document.createElement('section');
        oc.className = 'story-section';
        const oh = document.createElement('h2');
        oh.textContent = 'Outcome';
        oc.appendChild(oh);
        ['short_term','long_term'].forEach(k => {
          if (data.outcome[k]) {
            const p = document.createElement('p');
            p.textContent = data.outcome[k];
            oc.appendChild(p);
          }
        });
        main.appendChild(oc);
      }
      // Put summary section first
      main.insertBefore(summarySection, main.firstChild);
    }

  } catch (err) {
    console.error(err);
    const main = document.getElementById('story-content');
    main.textContent = 'Error cargando la historia.';
  }
}

loadHistoria();
