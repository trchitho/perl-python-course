function submitForm(event) {
  event.preventDefault(); // Ngăn reload form

  const fullname = document.getElementById("fullname").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;

  // Nếu là giáo viên, lấy thêm department
  const data = { fullname, email, password, role };
  if (role === "teacher") {
    const department = document.getElementById("department").value;
    data.department = department;
  }

  fetch("http://127.0.0.1:5000/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("result").innerText = data.message;

      if (data.message === "Đăng ký thành công") {
        setTimeout(() => {
          window.location.href = "login.html";
        }, 1000); // Đợi 1 giây để người dùng thấy thông báo
      }
    })
    .catch(error => {
      console.error("Lỗi:", error);
      document.getElementById("result").innerText = "Có lỗi xảy ra.";
    });
}

// Hiện/ẩn trường department khi chọn vai trò
document.getElementById("role").addEventListener("change", function () {
  const deptField = document.getElementById("departmentField");
  if (this.value === "teacher") {
    deptField.style.display = "block";
    document.getElementById("department").setAttribute("required", true);
  } else {
    deptField.style.display = "none";
    document.getElementById("department").removeAttribute("required");
  }
});
