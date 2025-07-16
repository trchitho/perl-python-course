document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const lessonId = new URLSearchParams(window.location.search).get("lesson_id");

  if (!token) {
    alert("Bạn cần đăng nhập.");
    return;
  }

  fetch("http://localhost:5000/api/student/assignments", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(res => {
      if (!res.ok) throw new Error("Không thể tải bài tập");
      return res.json();
    })
    .then(assignments => {
      const list = document.getElementById("assignment-list");
      list.innerHTML = "";

      assignments.forEach(ass => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
          <h3>${ass.title}</h3>
          <p>${ass.description}</p>
          <p><strong>🕒 Deadline:</strong> ${new Date(ass.deadline).toLocaleString()}</p>
          <button class="btn-view" onclick="toggleIDE(${ass.id})">▶️ Làm bài</button>
          <div id="ide-${ass.id}" style="display:none; margin-top:15px;"></div>
        `;
        list.appendChild(card);
      });

      // ✅ Sau khi render hết bài tập, thêm nút "Học tiếp" nếu có lesson_id
      if (lessonId) {
        const backBtn = document.createElement("div");
        backBtn.style.marginTop = "30px";
        backBtn.innerHTML = `
          <a href="../khoahoc/baihoc.html?lesson_id=${lessonId}" class="btn-next">📚 Học tiếp</a>
        `;
        list.appendChild(backBtn);
      }
    })
    .catch(err => {
      console.error("Lỗi khi tải bài tập:", err);
    });
});

function toggleIDE(assignmentId) {
  const ideDiv = document.getElementById(`ide-${assignmentId}`);

  if (ideDiv.innerHTML !== "") {
    ideDiv.style.display = ideDiv.style.display === "none" ? "block" : "none";
    return;
  }

  ideDiv.innerHTML = `
    <div class="editor">
      <h4>✏️ Viết mã Python</h4>
      <textarea id="code-${assignmentId}" rows="10" placeholder="# Viết mã Python tại đây..."></textarea>
    </div>

    <button onclick="runCode(${assignmentId})" class="btn-view">▶️ Chạy chương trình</button>

    <div class="stdout">
      <h4>📤 Kết quả</h4>
      <pre id="output-${assignmentId}"></pre>
    </div>
  `;
  ideDiv.style.display = "block";
}

function runCode(assignmentId) {
  const code = document.getElementById(`code-${assignmentId}`).value;
  const outputEl = document.getElementById(`output-${assignmentId}`);

  fetch("https://emkc.org/api/v2/piston/execute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      language: "python",
      version: "3.10.0",
      files: [{ name: "main.py", content: code }]
    })
  })
    .then(res => res.json())
    .then(result => {
      if (result.run.stderr) {
        outputEl.textContent = `❌ Lỗi:\n${result.run.stderr}`;
      } else {
        outputEl.textContent = `✅ Kết quả:\n${result.run.output}`;
      }
    })
    .catch(err => {
      outputEl.textContent = "❌ Lỗi khi gửi yêu cầu: " + err;
    });
}
