import { listCourseQuizzes, getQuiz, submitQuiz as submitQuizAPI, getCourseDetail } from '/frontend/services/studentAPI.js';
import { listAllCourses } from '/frontend/services/courseAPI.js';

const params = new URLSearchParams(window.location.search);
const token = localStorage.getItem('token');
const courseId = params.get('course_id');
const quizId = params.get('quiz_id');

document.getElementById('back-to-lesson').href = courseId ? `/frontend/pages/student/lessons.html?course_id=${courseId}` : '/frontend/pages/student/lessons.html';

const storageKey = `quiz_${quizId||courseId||'unknown'}_answers`;
const pendingKey = `quiz_${quizId||courseId||'unknown'}_pending_submit`;
const redoKey = `quiz_${quizId||courseId||'unknown'}_submitted`;
const orderKey = `quiz_${quizId||courseId||'unknown'}_order`;

async function renderQuizSelection() {
  const container = document.getElementById('quiz');
  container.innerHTML = '<div class="card">Loading your courses...</div>';
  try {
    const courses = (await listAllCourses(token)).filter(c => c.enrolled);
    if(!courses.length){
      container.innerHTML = '<div class="card">Bạn chưa đăng ký khóa học nào. Ghé <a href="/frontend/pages/student/courses.html">Courses</a> để đăng ký.</div>';
      return;
    }
    const sections = await Promise.all(courses.map(async course => {
      const [detail, quizzes] = await Promise.all([
        getCourseDetail(token, course.id),
        listCourseQuizzes(token, course.id)
      ]);
      const lessonQuizzes = {};
      const uncategorized = [];
      (quizzes||[]).forEach(q => {
        if(q.lesson_id){
          lessonQuizzes[q.lesson_id] = lessonQuizzes[q.lesson_id] || [];
          lessonQuizzes[q.lesson_id].push(q);
        }else{
          uncategorized.push(q);
        }
      });
        const lessonList = (detail.lessons||[]).map(lesson => {
          const qList = lessonQuizzes[lesson.id] || [];
          return `<li class="lesson-row" data-course="${course.id}" data-lesson="${lesson.id}" data-quiz="${qList[0]?.id||''}" data-count="${qList.length}" style="cursor:pointer;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
            <div>
              <strong>${lesson.title||'Lesson'}</strong>
              <div style="color:#6b7280;font-size:12px;">${lesson.description||''}</div>
            </div>
            <div style="text-align:right">
              <div>${qList.length} quiz${qList.length===1?'':'es'}</div>
              ${qList.length ? `<span style="font-size:12px;color:#10b981">Click để làm quiz</span>` : ''}

            </div>
          </div>
        </li>`;
      }).join('');
      const extraBlock = uncategorized.length ? `
        <li class="lesson-row uncategorized" data-course="${course.id}" data-lesson="" data-quiz="${uncategorized[0].id}" style="cursor:pointer;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
            <div>
              <strong>Quiz không gắn tiết học</strong>
              <div style="color:#6b7280;font-size:12px;">${uncategorized.length} quiz</div>
            </div>
            <div style="text-align:right"><span style="font-size:12px;color:#10b981">Click để làm quiz</span></div>
          </div>
        </li>` : '';
      const lessonMarkup = ((lessonList || '') + extraBlock) || '<li>No lessons yet.</li>';
      return `<div class="card course-card" data-course="${course.id}" style="margin-bottom:12px;">
        <div class="course-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:12px;cursor:pointer;">
          <div>
            <h3 style="margin:0;">${course.name||('Course #'+course.id)}</h3>
            <div style="color:#6b7280;font-size:12px;">${course.description||''}</div>
          </div>
          <div style="display:flex;flex-direction:column;align-items:flex-end;font-size:14px;">
            <span>${detail.lessons?.length || 0} lessons</span>
            <span>${(quizzes||[]).length} quizzes</span>
          </div>
        </div>
        <details class="lesson-panel" data-panel style="margin-bottom:8px;">
          <summary class="lesson-toggle w3-button w3-small w3-outline" style="display:inline-block;">Hiện bài học</summary>
          <ul class="simple-list" style="margin:0">${lessonMarkup}</ul>
          <div class="lesson-detail card" style="margin-top:12px;display:none;"></div>
        </details>
      </div>`;
    }));
    container.innerHTML = sections.join('');
    container.querySelectorAll('.lesson-panel').forEach(panel=>{
      panel.addEventListener('toggle', ()=>{
        const summary = panel.querySelector('.lesson-toggle');
        if(summary){
          summary.textContent = panel.open ? 'Ẩn bài học' : 'Hiện bài học';
        }
      });
    });
    container.querySelectorAll('.course-header').forEach(header=>{
      header.addEventListener('click', ()=>{
        const panel = header.parentElement.querySelector('.lesson-panel');
        if(panel) panel.open = !panel.open;
      });
    });
    container.querySelectorAll('.lesson-row').forEach(row=>{
      row.addEventListener('click', async (e)=>{
        e.preventDefault();
        const lessonId = row.dataset.lesson;
        const lessonQuiz = row.dataset.quiz;
        const course = row.dataset.course;
        const card = row.closest('.card');
        const detailPanel = card.querySelector('.lesson-detail');
        const panel = card.querySelector('.lesson-panel');
        if(!detailPanel || !panel) return;
        panel.open = true;
        if(!lessonId){
          if(lessonQuiz){
            location.href = `?course_id=${course}&quiz_id=${lessonQuiz}`;
          }
          return;
        }
        detailPanel.innerHTML = '<div class="card">Loading lesson...</div>';
        detailPanel.style.display = 'block';
        try{
          const lesson = await getLessonDetail(token, lessonId);
          detailPanel.innerHTML = `
            <h4 style="margin-top:0;">${lesson.title||'Lesson'}</h4>
            <div style="color:#6b7280;font-size:13px;margin-bottom:8px;">${lesson.content?lesson.content.replace(/\n/g,'<br>'):'Không có nội dung'}</div>
            ${lesson.video_url?renderMedia(lesson.video_url):''}
            ${lessonQuiz ? `<div style="margin-top:8px;"><a class="w3-button w3-small" href="?course_id=${course}&quiz_id=${lessonQuiz}">Làm quiz cho tiết này</a></div>` : '<div style="margin-top:8px;color:#9ca3af;">Chưa có quiz</div>'}
          `;
        }catch(e){
          detailPanel.innerHTML = '<div class="card">Không tải được nội dung.</div>';
        }
      });
    });
  }catch(e){
    container.innerHTML = '<div class="card">Không tải được danh sách khóa học.</div>';
  }
}

function shuffle(arr){
  const a = [...arr];
  for(let i=a.length-1;i>0;i--){
    const j = Math.floor(Math.random()*(i+1));
    [a[i],a[j]]=[a[j],a[i]];
  }
  return a;
}

async function renderQuiz(quizId){
  const container = document.getElementById('quiz');
  container.innerHTML = '<div class="card">Loading quiz...</div>';
  try{
    const quiz = await getQuiz(token, quizId);
    container.innerHTML = '';
    container.onchange = null;
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
    let order = JSON.parse(localStorage.getItem(orderKey) || 'null');
    if(!order){
      order = shuffle((quiz||[]).map(q=>({
        id: q.id,
        options: shuffle(['A','B','C','D'].filter(opt => q[`option_${opt.toLowerCase()}`]))
      })));
      localStorage.setItem(orderKey, JSON.stringify(order));
    }
    const quizMap = new Map((quiz||[]).map(q=>[q.id,q]));
    const orderedQuiz = order.map(o=>{
      const original = quizMap.get(o.id);
      if(!original) return null;
      return {...original, __optionOrder: o.options};
    }).filter(Boolean);
    const isLocked = Boolean(localStorage.getItem(redoKey));
    container.classList.toggle('quiz-locked', isLocked);
    (orderedQuiz||[]).forEach(q => {
      const wrap = document.createElement('div');
      wrap.className = 'card quiz-card';
      wrap.innerHTML = `<h3>${q.question_text}</h3>`;
      const optionOrder = q.__optionOrder || ['A','B','C','D'];
      optionOrder.forEach(label => {
        const text = q[`option_${label.toLowerCase()}`];
        if(!text) return;
        const checked = saved[q.id] === label ? 'checked' : '';
        wrap.innerHTML += `
          <label style="display:block;margin:4px 0;">
            <input type="radio" name="q_${q.id}" value="${label}" ${checked}/> ${label}. ${text}
          </label>`;
      });
      if(isLocked){
        wrap.style.pointerEvents = 'none';
        wrap.style.opacity = '0.75';
        wrap.querySelectorAll('input[type=radio]').forEach(inp=>inp.disabled = true);
      }
      container.appendChild(wrap);
    });
    container.onchange = () => {
      const answers = {};
      container.querySelectorAll('input[type=radio]:checked').forEach(inp => {
        const qid = parseInt(inp.name.split('_')[1]);
        answers[qid] = inp.value;
      });
      localStorage.setItem(storageKey, JSON.stringify(answers));
      document.getElementById('status').textContent = 'Đã lưu tạm thời';
    };
    if(Object.keys(saved).length){
      document.getElementById('status').textContent = 'Đã khôi phục bài làm trước đó.';
    } else {
      document.getElementById('status').textContent = '';
    }
  }catch(e){ container.innerHTML = '<div class="card">Không tải được quiz.</div>'; }
}

async function submitQuiz(){
  const container = document.getElementById('quiz');
  const answers = {};
  container.querySelectorAll('input[type=radio]:checked').forEach(inp => {
    const qid = parseInt(inp.name.split('_')[1]);
    answers[qid] = inp.value;
  });
  localStorage.setItem(storageKey, JSON.stringify(answers));
  try{
    if(!quizId) throw new Error('no quiz');
    const result = await submitQuizAPI(token, quizId, answers);
    localStorage.removeItem(pendingKey);
    localStorage.setItem(redoKey, '1');
    document.getElementById('quiz').classList.add('quiz-locked');
    document.getElementById('status').textContent = `Bạn đã nộp bài. Điểm: ${result.score}`;
    document.getElementById('redo').style.display = 'inline-block';
    document.getElementById('submit').disabled = true;
  }catch(e){
    localStorage.setItem(pendingKey, '1');
    document.getElementById('status').textContent = 'Lỗi mạng. Sẽ tự nộp khi online.';
  }
}

window.addEventListener('online', async () => {
  if (localStorage.getItem(pendingKey) && quizId) {
    await submitQuiz();
  }
});

document.getElementById('submit').addEventListener('click', submitQuiz);
document.getElementById('redo').addEventListener('click', async ()=>{
  localStorage.removeItem(storageKey);
  localStorage.removeItem(redoKey);
  localStorage.removeItem(orderKey);
  document.getElementById('submit').disabled = false;
  document.getElementById('redo').style.display = 'none';
  document.getElementById('status').textContent = 'Bạn có thể làm lại.';
  if(quizId){
    await renderQuiz(quizId);
  }
});

(async ()=>{
  if(quizId){
    await renderQuiz(quizId);
    if(localStorage.getItem(redoKey)){
      document.getElementById('submit').disabled = true;
      document.getElementById('redo').style.display = 'inline-block';
      document.getElementById('status').textContent = 'Bạn đã nộp bài. Có thể nhấn "Làm lại" để thi lại.';
    }
  } else {
    await renderQuizSelection();
  }
})();
