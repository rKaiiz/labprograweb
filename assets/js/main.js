// Shared UI + state (localStorage based)
(function(){
  const STORAGE_KEYS = {
    cart: 'lmd_cart',
    reviews: 'lmd_reviews'
  };
  const qs = (sel, el=document) => el.querySelector(sel);
  const qsa = (sel, el=document) => Array.from(el.querySelectorAll(sel));

  function getCart(){
    try{ return JSON.parse(localStorage.getItem(STORAGE_KEYS.cart) || '[]'); }catch{ return [] }
  }
  function setCart(cart){ localStorage.setItem(STORAGE_KEYS.cart, JSON.stringify(cart)); dispatchEvent(new CustomEvent('cart:changed')); }
  function cartCount(){ return getCart().reduce((a,i)=>a+i.qty,0); }

  function addToCart(id, qty=1){
    const cart = getCart();
    const found = cart.find(i=>i.id===id);
    if(found) found.qty += qty; else cart.push({id, qty});
    setCart(cart);
  }
  function updateQty(id, delta){
    const cart = getCart();
    const item = cart.find(i=>i.id===id);
    if(!item) return;
    item.qty += delta;
    if(item.qty<=0){
      const i = cart.indexOf(item); cart.splice(i,1);
    }
    setCart(cart);
  }
  function removeFromCart(id){ setCart(getCart().filter(i=>i.id!==id)); }

  // Layout rendering
  function renderLayout(){
    const page = document.body.dataset.page || '';
    const app = document.createElement('div');
    app.className = 'app';

    const sidebar = document.createElement('nav');
    sidebar.className = 'sidebar';
    sidebar.innerHTML = `
      <a href="index.html" class="${page==='inicio'?'active':''}">Inicio</a>
      <a href="menu.html" class="${page==='menu'?'active':''}">Menu</a>
      <a href="pedidos.html" class="${page==='pedidos'?'active':''}">Carritos/pedidos <span class="badge" id="navCart"></span></a>
      <a href="resenas.html" class="${page==='resenas'?'active':''}">Reseñas</a>
      <a href="acerca.html" class="${page==='acerca'?'active':''}">Acerca de nosotros</a>
      <a href="contacto.html" class="${page==='contacto'?'active':''}">Contacto</a>
    `;

    const header = document.createElement('header');
    header.className = 'header';
    header.textContent = (qs('title')?.textContent) || 'La Media Docena';

    const main = document.createElement('main');
    const existing = qs('main');
    if(existing){
      // If developer already has a main tag, keep it
      existing.classList.add('container');
      app.append(sidebar, header, existing);
    } else {
      main.className = 'container';
      main.innerHTML = '<p>Contenido</p>';
      app.append(sidebar, header, main);
      document.body.append(app);
    }

    document.body.prepend(app);
    // Move original body children inside main (except the app itself)
    const children = qsa('body > :not(.app)');
    children.forEach(ch=> main.appendChild(ch));

    function updateNavCart(){ const badge=qs('#navCart'); if(badge){ const c=cartCount(); badge.style.display=c?"inline-block":"none"; badge.textContent=c; } }
    updateNavCart();
    addEventListener('cart:changed', updateNavCart);
  }

  // Public API
  window.$app = {
    addToCart, updateQty, removeFromCart, getCart, setCart,
    findProduct(id){ return (window.APP_DATA?.products||[]).find(p=>p.id===id); },
    formatCurrency(n){ return new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n); },
  };

  document.addEventListener('DOMContentLoaded', renderLayout);
})();
