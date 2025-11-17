// Shared top navigation behavior (W3Schools-like)
(function(){
  function init(){
    var mobileBtn = document.querySelector('#w3MenuBtn');
    var panel = document.querySelector('#w3MobilePanel');
    if(mobileBtn && panel){
      mobileBtn.addEventListener('click', function(){
        panel.classList.toggle('open');
      });
    }
    // Auth/UI state
    var token = localStorage.getItem('token');
    var role = localStorage.getItem('role');
    var navLogin = document.querySelector('#navLogin');
    var navSignup = document.querySelector('#heroSignup');
    var navDash = document.querySelector('#navDashboard');
    var navLogout = document.querySelector('#navLogout');
    var mobileLogin = document.querySelector('#mNavLogin');
    var mobileDash = document.querySelector('#mNavDashboard');
    var mobileLogout = document.querySelector('#mNavLogout');
    if(token){
      if(navLogin) navLogin.style.display = 'none';
      if(navSignup) navSignup.style.display = 'none';
      if(mobileLogin) mobileLogin.style.display = 'none';
      if(navDash){
        var href = '/frontend/index.html';
        if(role === 'teacher') href = '/frontend/pages/teacher/dashboard.html';
        else if(role === 'admin') href = '/frontend/pages/admin/dashboard.html';
        navDash.href = href; navDash.style.display = 'inline-block';
        if(mobileDash){
          mobileDash.href = href;
          mobileDash.style.display = 'block';
        }
      }
      if(navLogout){
        navLogout.style.display = 'inline-block';
        navLogout.addEventListener('click', function(e){
          e.preventDefault();
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          localStorage.removeItem('fullname');
          location.href = '/frontend/index.html';
        }, { once: true });
        if(mobileLogout){
          mobileLogout.style.display = 'block';
          mobileLogout.addEventListener('click', function(e){
            e.preventDefault();
            localStorage.removeItem('token');
            localStorage.removeItem('role');
            localStorage.removeItem('fullname');
            location.href = '/frontend/index.html';
          }, { once: true });
        }
      }
    }
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();



