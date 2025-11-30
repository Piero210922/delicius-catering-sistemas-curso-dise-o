(function(){
  function matchHeroHeight(){
    var card = document.getElementById('auth-card');
    var img = document.getElementById('hero-graphic');
    if(!card || !img) return;
    if(window.matchMedia('(max-width:900px)').matches){
      img.style.height = '';
      return;
    }
    var h = Math.ceil(card.getBoundingClientRect().height);
    img.style.height = h + 'px';
  }
  window.addEventListener('load', matchHeroHeight);
  window.addEventListener('resize', matchHeroHeight);
  // also run after fonts/images load (in case card size changes)
  window.addEventListener('DOMContentLoaded', function(){ setTimeout(matchHeroHeight, 50); });
})();
