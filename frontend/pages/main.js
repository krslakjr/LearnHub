function loadMenu() {
    fetch('Meni.html')
      .then(response => response.text())
      .then(data => {
        document.getElementById('meni-placeholder').innerHTML = data;
  
        updateNavButtons();
      })
      .catch(error => {
        console.error('Greška pri učitavanju menija:', error);
      });
  }
  
  function updateNavButtons() {
    const navButtons = document.getElementById('nav-buttons');
    if (!navButtons) return;
  
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    
    if (isLoggedIn) {
      navButtons.innerHTML = `
        <div class="user-info">
          <img src="../img/user.png" alt="User Image" class="user-img" />
          <button onclick="logout()">Logout</button>
        </div>
      `;
    } else {
      navButtons.innerHTML = `
        <a href="Login.html"><button>Login</button></a>
        <a href="Register.html"><button>Register</button></a>
      `;
    }
  }
  
  function logout() {
    localStorage.setItem('loggedIn', 'false');
    window.location.href = "index.html";
  }
  

  function enroll() {
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    if (!isLoggedIn) {
      window.location.href = "Login.html";
      return;
    }
  
    enrolled = true;
    populateSidebar();
    showSection('modules');
  }
  
  function unenroll() {
    enrolled = false;
    populateSidebar();
    showSection('overview');
  }
  
  
  document.addEventListener('DOMContentLoaded', loadMenu);
  