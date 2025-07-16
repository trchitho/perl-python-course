document.getElementById('loginForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
      document.getElementById('result').innerText = '✅ Đăng nhập thành công! Xin chào ' + data.fullname;

      localStorage.setItem('token', data.token);
      localStorage.setItem('role', data.role);

      // 🔁 Chuyển hướng theo role
      setTimeout(() => {
        if (data.role === 'admin') {
          window.location.href = '#';
        } else if (data.role === 'teacher') {
          window.location.href = '../trangchinh/giangvien/index.html';
        } else if (data.role === 'student') {
          window.location.href = '../trangchinh/sinhvien/index.html';
        } else {
          window.location.href = 'error.html';  // fallback nếu role lạ
        }
      }, 1000);
    } else {
      document.getElementById('result').innerText = '❌ ' + (data.message || 'Đăng nhập thất bại!');
    }
  } catch (err) {
    document.getElementById('result').innerText = 'Lỗi kết nối server';
    console.error(err);
  }
});
