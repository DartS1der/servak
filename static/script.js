// Загрузка списка кормушек
async function loadFeeders() {
    const response = await fetch('/api/feeders');
    
    if (response.status === 401) {
        window.location.href = '/login';
        return;
    }
    
    const data = await response.json();
    const container = document.getElementById('feeder-items');
    container.innerHTML = '';
    
    data.feeders.forEach(feeder => {
        const div = document.createElement('div');
        div.className = 'feeder-item';
        div.innerHTML = `
            <h3>${feeder.name}</h3>
            <button onclick="editFeeder(${feeder.id})">Настроить</button>
        `;
        container.appendChild(div);
    });
}

// Показ формы добавления
function showAddFeederForm() {
    const form = `
        <div class="feeder-form">
            <input type="text" id="feeder-name" placeholder="Название">
            <textarea id="feeder-schedule" placeholder="Расписание (JSON)"></textarea>
            <button onclick="addFeeder()">Сохранить</button>
        </div>
    `;
    document.getElementById('feeder-items').innerHTML = form;
}

// Добавление новой кормушки
async function addFeeder() {
    const feederData = {
        name: document.getElementById('feeder-name').value,
        schedule: document.getElementById('feeder-schedule').value
    };
    
    await fetch('/api/feeders', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(feederData)
    });
    
    loadFeeders();
}

// Загружаем данные при старте
loadFeeders();
