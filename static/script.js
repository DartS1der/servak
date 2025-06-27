// Загружаем расписание с сервера
async function loadSchedule() {
    const response = await fetch('/api/schedule');
    const data = await response.json();
    
    const list = document.getElementById('schedule-list');
    list.innerHTML = '';
    
    data.schedule.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `⏰ ${item.time} → ${item.grams} грамм`;
        list.appendChild(li);
    });
}

// Обновляем данные каждые 5 секунд
loadSchedule();
setInterval(loadSchedule, 5000);
