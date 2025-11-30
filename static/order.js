// order wizard JS: step navigation, package selection, counters and summary
document.addEventListener('DOMContentLoaded', function(){
  const steps = Array.from(document.querySelectorAll('.step-content'));
  const progressSteps = Array.from(document.querySelectorAll('.progress-step'));
  const toStep2 = document.getElementById('toStep2');
  const toStep3 = document.getElementById('toStep3');
  const toStep4 = document.getElementById('toStep4');
  const backTo1 = document.getElementById('backTo1');
  const backTo2 = document.getElementById('backTo2');
  const backTo3 = document.getElementById('backTo3');

  function showStep(n){
    steps.forEach(s=> s.classList.toggle('active', s.dataset.step==String(n)));
    progressSteps.forEach(p=> p.classList.toggle('active', p.dataset.step==String(n)));
  }

  // package selection: listen for changes on radio inputs
  document.querySelectorAll('input[name="id_paquete"]').forEach(inp=>{
    inp.addEventListener('change', ()=>{
      // clear selection visuals
      document.querySelectorAll('.package-select-card').forEach(l=> l.classList.remove('selected'));
      const lab = inp.closest('.package-select-card');
      if(lab) lab.classList.add('selected');
      updateSummary();
    });
    // initialize visual selection
    if(inp.checked){
      const lab = inp.closest('.package-select-card'); if(lab) lab.classList.add('selected');
    }
  });

  // unified counter buttons handler: works for guest counter and small menu counters
  document.querySelectorAll('button[data-action]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const action = btn.dataset.action;
      // find the nearest counter container that has an input
      const container = btn.closest('.counter-control') || btn.parentElement;
      const input = container ? container.querySelector('input[type=number]') : null;
      if(!input) return;
      let val = parseInt(input.value||0);
      const min = input.hasAttribute('min') ? parseInt(input.getAttribute('min')) : 0;
      if(action=='increase') val++; else val = Math.max(min, val-1);
      input.value = val;
      // if this is the invitados input, update summary
      if(input.id === 'invitados'){ updateSummary(); }
      // if counters changed, update addons display as well (some counters are in menus)
      updateAddonsDisplay();
    });
  });

  function getSelectedPackage(){
    const sel = document.querySelector('input[name="id_paquete"]:checked');
    if(!sel) return null;
    const name = sel.dataset.name || sel.getAttribute('data-name') || '';
    const price = parseFloat(sel.dataset.price || sel.getAttribute('data-price') || 0);
    return {id: sel.value, name: name, price: price};
  }

  // helper: retrieve integer value from multiple possible input name variants
  function intFromNames(names){
    for(const n of names){
      const el = document.querySelector(`input[name="${n}"]`);
      if(el) return parseInt(el.value||0);
    }
    return 0;
  }

  function showStep1Error(show, message){
    const el = document.getElementById('step1Error');
    if(!el) return;
    el.style.display = show ? 'block' : 'none';
    if(message) el.textContent = message;
  }

  function sumMenus(){
    // accept both lowercase and capitalized input names (server accepts both)
    const normal = intFromNames(['menu_normal','menu_Normal','menu_NORMAL','menu_Normal']);
    const veg = intFromNames(['menu_vegano','menu_Vegano','menu_VEGANO']);
    const cel = intFromNames(['menu_celiaco','menu_Celíaco','menu_CELIACO']);
    const ale = intFromNames(['menu_alergico','menu_Alérgico','menu_ALERGICO']);
    return normal + veg + cel + ale;
  }

  function updateSummary(){
    const pkg = getSelectedPackage();
    const invitados = parseInt(document.getElementById('invitados').value||0);
    if(pkg){
      const sp = document.getElementById('summaryPaquete'); if(sp) sp.textContent = pkg.name;
      const sprice = document.getElementById('summaryPrecio'); if(sprice) sprice.textContent = pkg.price.toFixed(2);
      const sinv = document.getElementById('summaryInvitados'); if(sinv) sinv.textContent = invitados;
      const subtotal = (pkg.price * invitados);
      const ssub = document.getElementById('summarySubtotal'); if(ssub) ssub.textContent = subtotal.toFixed(2);
      const step1sub = document.getElementById('step1Subtotal'); if(step1sub) step1sub.textContent = `S/. ${subtotal.toFixed(2)}`;
    }
  }

  // calculate addons subtotal using data-price and data-fixed attributes
  function calculateAddonsSubtotal(){
    const invitados = parseInt(document.getElementById('invitados').value||0);
    let subtotal = 0;
    document.querySelectorAll('.addons-grid input[type=checkbox]').forEach(ch=>{
      if(!ch.checked) return;
      const price = parseFloat(ch.dataset.price || ch.getAttribute('data-price') || 0) || 0;
      // Treat all adicionales as fixed one-time fees (not per-person)
      subtotal += price;
    });
    return subtotal;
  }

  function updateAddonsDisplay(){
    const subtotal = calculateAddonsSubtotal();
    const el = document.getElementById('addonsSubtotal'); if(el) el.textContent = `S/. ${subtotal.toFixed(2)}`;
  }

  function showMenuError(show){
    const el = document.getElementById('menuError');
    if(!el) return;
    el.style.display = show ? 'block' : 'none';
  }

  // navigation handlers
  if(toStep2) toStep2.addEventListener('click', ()=>{
    // validate that a package is selected and a date is chosen before moving to menus
    const pkg = getSelectedPackage();
    const fecha = document.querySelector('input[name="fecha_evento"]');
    const invitadosVal = parseInt(document.getElementById('invitados').value||0);
    if(!pkg){
      showStep1Error(true, 'Debe seleccionar un paquete para continuar.');
      return;
    }
    if(!fecha || !fecha.value){
      showStep1Error(true, 'Debe seleccionar la fecha del evento.');
      return;
    }
    if(!invitadosVal || invitadosVal < 5){
      showStep1Error(true, 'La cantidad de invitados debe ser al menos 5.');
      return;
    }
    showStep1Error(false);
    updateSummary();
    showStep('2');
  });
  if(backTo1) backTo1.addEventListener('click', ()=> showStep('1'));
  if(toStep3) toStep3.addEventListener('click', ()=>{
    // validate menus before allowing to proceed
    const invitados = parseInt(document.getElementById('invitados').value||0);
    if(!invitados || invitados < 5){
      showStep1Error(true, 'La cantidad de invitados debe ser al menos 5.');
      showStep('1');
      return;
    }
    const totalMenus = sumMenus();
    // Require that the sum of special menus matches the number of guests
    if(totalMenus !== invitados){
      showMenuError(true);
      return; // block navigation
    }
    showMenuError(false);
    showStep('3');
  });
  if(backTo2) backTo2.addEventListener('click', ()=> showStep('2'));
  if(toStep4) toStep4.addEventListener('click', ()=>{
    // validate menus again before final summary
    const invitados = parseInt(document.getElementById('invitados').value||0);
    if(!invitados || invitados < 5){
      showStep1Error(true, 'La cantidad de invitados debe ser al menos 5.');
      showStep('1');
      return;
    }
    const totalMenus = sumMenus();
    if(totalMenus !== invitados){
      showMenuError(true);
      // switch to step 2 so user can fix
      showStep('2');
      return;
    }
    showMenuError(false);
    // populate final summary
    populateFinal();
    showStep('4');
  });
  if(backTo3) backTo3.addEventListener('click', ()=> showStep('3'));

  function populateFinal(){
    updateSummary();
    const pkg = getSelectedPackage();
    const invitados = parseInt(document.getElementById('invitados').value||0);
    const elFinalPaquete = document.getElementById('finalPaquete'); if(elFinalPaquete) elFinalPaquete.textContent = pkg ? pkg.name : '-';
    const elFinalPrecioBase = document.getElementById('finalPrecioBase'); if(elFinalPrecioBase) elFinalPrecioBase.textContent = pkg ? `S/. ${ (pkg.price).toFixed(2) }` : 'S/. 0.00';
    const elFinalInv = document.getElementById('finalInvitados'); if(elFinalInv) elFinalInv.textContent = invitados;

    // menus (support multiple name variants)
    const veg = intFromNames(['menu_vegano','menu_Vegano','menu_VEGANO']);
    const cel = intFromNames(['menu_celiaco','menu_Celíaco','menu_CELIACO']);
    const ale = intFromNames(['menu_alergico','menu_Alérgico','menu_ALERGICO']);
    const totalMenus = veg + cel + ale;
    const fm = document.getElementById('finalMenusText'); if(fm) fm.innerHTML = `<strong>Menús Especiales:</strong> Veganos(${veg}), Celíacos(${cel}), Alérgicos(${ale}) — Total: ${totalMenus}`;

    // adicionales
    // build list of selected adicionales with prices
    const addons = Array.from(document.querySelectorAll('.addons-grid input[type=checkbox]:checked'));
    const addonLines = addons.map(ch=>{
      const label = ch.closest('label');
      const name = label ? (label.querySelector('.addon-details h5') ? label.querySelector('.addon-details h5').textContent.trim() : label.textContent.trim()) : ch.value;
      const price = parseFloat(ch.dataset.price || ch.getAttribute('data-price') || 0) || 0;
      // All adicionales treated as fixed one-time fees
      const linePrice = price;
      return {name, price: linePrice, displayPrice: linePrice};
    });

    const fa = document.getElementById('finalAdicionalesList');
    if(fa){
      if(addonLines.length === 0) fa.innerHTML = `<strong>Adicionales:</strong> Ninguno`;
      else fa.innerHTML = `<strong>Adicionales:</strong><ul style="margin:6px 0;padding-left:18px">` + addonLines.map(a=>`<li>${a.name} — S/. ${a.displayPrice.toFixed(2)}</li>`).join('') + `</ul>`;
    }

    // calculate totals: base + adicionales
    let total = 0;
    if(pkg) total += pkg.price * invitados;
    total += addonLines.reduce((s,a)=> s + a.price, 0);

    const ftotal = document.getElementById('finalTotal'); if(ftotal) ftotal.textContent = total.toFixed(2);
  }

  // on-submit validation: re-check everything before allowing the form to submit
  const orderForm = document.getElementById('orderForm');
  if(orderForm){
    orderForm.addEventListener('submit', function(ev){
      // Validate package
      const pkg = getSelectedPackage();
      if(!pkg){
        showStep1Error(true, 'Debe seleccionar un paquete antes de enviar.');
        showMenuError(false);
        ev.preventDefault();
        document.getElementById('step1Error').scrollIntoView({behavior:'smooth',block:'center'});
        return false;
      }

      // Validate fecha
      const fecha = document.querySelector('input[name="fecha_evento"]');
      if(!fecha || !fecha.value){
        showStep1Error(true, 'Debe seleccionar la fecha del evento antes de enviar.');
        ev.preventDefault();
        document.getElementById('step1Error').scrollIntoView({behavior:'smooth',block:'center'});
        return false;
      }

      // Validate invitados (minimum 5)
      const invitados = parseInt(document.getElementById('invitados').value||0);
      if(!invitados || invitados < 5){
        showStep1Error(true, 'Número de invitados inválido. Debe ser al menos 5.');
        ev.preventDefault();
        document.getElementById('step1Error').scrollIntoView({behavior:'smooth',block:'center'});
        return false;
      }

      // Validate menus equality
      const totalMenus = sumMenus();
      if(totalMenus !== invitados){
        showMenuError(true);
        ev.preventDefault();
        document.getElementById('menuError').scrollIntoView({behavior:'smooth',block:'center'});
        return false;
      }

      // All good; allow submit. Optionally, disable submit button to avoid double submit
      const submitBtn = orderForm.querySelector('button[type="submit"]');
      if(submitBtn) submitBtn.disabled = true;
      return true;
    });
  }

  // listen for addon checkbox changes to update subtotal and final
  document.querySelectorAll('.addons-grid input[type=checkbox]').forEach(ch=>{
    ch.addEventListener('change', ()=>{
      updateAddonsDisplay();
      updateSummary();
    });
  });

  // update in real-time when the invitados input changes (typing) so subtotals recalc
  const invitadosInput = document.getElementById('invitados');
  if(invitadosInput){
    invitadosInput.addEventListener('input', ()=>{
      // keep numeric sanity and validate minimum
      let val = parseInt(invitadosInput.value||0);
      if(isNaN(val)) val = 0;
      // do not override user's typing aggressively; show error if below min
      if(val < 5){
        showStep1Error(true, 'La cantidad de invitados debe ser al menos 5.');
      } else {
        showStep1Error(false);
      }
      updateSummary();
      updateAddonsDisplay();
      // validate menus sum against invitados (only when invitados meets minimum)
      const totalMenus = sumMenus();
      if(val >= 6 && totalMenus !== val){ showMenuError(true); } else { showMenuError(false); }
    });
  }

  // update when any special menu numeric input changes
  document.querySelectorAll('.special-menus-list input[type=number]').forEach(mi=>{
    mi.addEventListener('input', ()=>{
      // normalize value
      let v = parseInt(mi.value||0);
      if(isNaN(v) || v < 0) v = 0;
      mi.value = v;
      const invitados = parseInt(document.getElementById('invitados').value||0);
      const totalMenus = sumMenus();
      if(invitados >= 5 && totalMenus !== invitados){ showMenuError(true); } else { showMenuError(false); }
    });
  });

  // initialize
  updateSummary();
  showStep('1');
});
