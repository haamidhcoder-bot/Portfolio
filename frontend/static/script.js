const menuBtn=document.querySelector('.menu-btn');
const nav=document.querySelector('.navbar nav');
menuBtn.addEventListener('click',()=>{nav.classList.toggle('open');});
document.querySelectorAll('nav a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));

const themeBtn=document.getElementById('themeBtn');
themeBtn.addEventListener('click',()=>{
  document.body.classList.toggle('light');
  themeBtn.textContent=document.body.classList.contains('light')?'☾':'☼';
});

const sections=[...document.querySelectorAll('main section')];
const links=[...document.querySelectorAll('nav a')];
const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+entry.target.id));
    }
  });
},{rootMargin:'-35% 0px -55% 0px'});
sections.forEach(s=>observer.observe(s));
