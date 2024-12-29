// DOM Elements
const scheduleModal = document.getElementById('scheduleModal');
const addScheduleBtn = document.getElementById('addScheduleBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const scheduleForm = document.getElementById('scheduleForm');
const schedulesList = document.getElementById('schedulesList');
const scheduleTypeSelect = document.querySelector('select[name="scheduleType"]');
const dayOfWeekField = document.getElementById('dayOfWeekField');
const statusMessage = document.getElementById('statusMessage');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load initial schedules
    loadSchedules();
    
    // Modal controls
    addScheduleBtn.addEventListener('click', () => {
        scheduleModal.classList.remove('hidden');
    });
    
    closeModalBtn.addEventListener('click', () => {
        scheduleModal.classList.add('hidden');
        scheduleForm.reset();
        dayOfWeekField.classList.add('hidden');
    });
    
    // Close modal when clicking outside
    scheduleModal.addEventListener('click', (e) => {
        if (e.target === scheduleModal) {
            scheduleModal.classList.add('hidden');
            scheduleForm.reset();
            dayOfWeekField.classList.add('hidden');
        }
    });
    
    // Toggle day of week field
    scheduleTypeSelect.addEventListener('change', () => {
        dayOfWeekField.classList.toggle('hidden', scheduleTypeSelect.value !== 'weekly');
    });
    
    // Handle form submission
    scheduleForm.addEventListener('submit', handleScheduleSubmit);
});

// Status message handling
function showMessage(message, isSuccess) {
    statusMessage.classList.remove('hidden');
    const messageText = statusMessage.querySelector('.message-text');
    messageText.textContent = message;
    
    statusMessage.className = `mb-8 ${isSuccess 
        ? 'bg-green-100 border border-green-400 text-green-700' 
        : 'bg-red-100 border border-red-400 text-red-700'} px-6 py-4 rounded-lg`;
    
    setTimeout(() => {
        statusMessage.classList.add('hidden');
    }, 5000);
}

// Source update functionality
async function runUpdate(source) {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Updating...';

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sources: [source] })
        });
        
        const result = await response.json();
        showMessage(
            result.status === 'success' 
                ? `Successfully updated ${source} portfolio data`
                : `Error updating ${source} portfolio data`,
            result.status === 'success'
        );
    } catch (error) {
        showMessage(`Error updating ${source} portfolio data`, false);
    } finally {
        button.disabled = false;
        button.textContent = 'Update Now';
    }
}

// Schedule handling
async function loadSchedules() {
    try {
        const response = await fetch('/api/schedules');
        const data = await response.json();
        
        if (data.status === 'success') {
            renderSchedules(data.schedules || []);
        }
    } catch (error) {
        showMessage('Error loading schedules', false);
    }
}

function renderSchedules(schedules) {
    if (!schedules.length) {
        schedulesList.innerHTML = '<p class="text-gray-500 text-center py-4">No schedules configured</p>';
        return;
    }

    schedulesList.innerHTML = schedules.map(schedule => `
        <div class="border rounded-lg p-4 bg-gray-50">
            <div class="flex justify-between items-center">
                <div>
                    <h3 class="text-lg font-medium text-gray-900">${schedule.name}</h3>
                    <p class="text-sm text-gray-600">
                        ${getScheduleTimeText(schedule)}
                    </p>
                    <p class="text-sm text-gray-600 mt-1">
                        Sources: ${schedule.selected_sources.join(', ')}
                    </p>
                </div>
                <div class="flex space-x-2">
                    <button onclick="toggleSchedule(${schedule.id}, ${!schedule.active})"
                            class="px-4 py-2 rounded-md text-sm ${
                                schedule.active 
                                    ? 'bg-red-600 hover:bg-red-700 text-white' 
                                    : 'bg-green-600 hover:bg-green-700 text-white'
                            }">
                        ${schedule.active ? 'Disable' : 'Enable'}
                    </button>
                    <button onclick="deleteSchedule(${schedule.id})"
                            class="px-4 py-2 rounded-md text-sm bg-gray-200 hover:bg-gray-300 text-gray-700">
                        Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function getScheduleTimeText(schedule) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return schedule.schedule_type === 'daily' 
        ? `Daily at ${schedule.time}`
        : `Weekly on ${days[schedule.day_of_week]} at ${schedule.time}`;
}

async function handleScheduleSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const selectedSources = Array.from(formData.getAll('sources'));
    
    if (!selectedSources.length) {
        showMessage('Please select at least one source', false);
        return;
    }
    
    const scheduleData = {
        name: formData.get('name'),
        schedule_type: formData.get('scheduleType'),
        time: formData.get('time'),
        selected_sources: selectedSources
    };
    
    if (formData.get('scheduleType') === 'weekly') {
        scheduleData.day_of_week = parseInt(formData.get('dayOfWeek'));
    }
    
    try {
        const response = await fetch('/api/schedules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scheduleData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            scheduleModal.classList.add('hidden');
            scheduleForm.reset();
            await loadSchedules();
            showMessage('Schedule created successfully', true);
        } else {
            throw new Error(result.message || 'Failed to create schedule');
        }
    } catch (error) {
        showMessage(error.message || 'Error creating schedule', false);
    }
}

async function toggleSchedule(scheduleId, active) {
    try {
        const response = await fetch(`/api/schedules/${scheduleId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            await loadSchedules();
            showMessage(`Schedule ${active ? 'enabled' : 'disabled'} successfully`, true);
        }
    } catch (error) {
        showMessage('Error updating schedule', false);
    }
}

async function deleteSchedule(scheduleId) {
    if (!confirm('Are you sure you want to delete this schedule?')) {
        return;
    }

    try {
        const response = await fetch(`/api/schedules/${scheduleId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            await loadSchedules();
            showMessage('Schedule deleted successfully', true);
        }
    } catch (error) {
        showMessage('Error deleting schedule', false);
    }
}