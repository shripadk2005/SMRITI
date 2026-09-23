/**
 * MINDCARE NER - Dashboard & Analytics Chart.js Loaders
 * Renders patient progress, caregiver monitoring telemetry, and admin analytics.
 */

function runDashboardInits() {
  if (typeof Chart === 'undefined') {
    setTimeout(runDashboardInits, 50);
    return;
  }
  initPatientDashboardChart();
  initCaregiverCharts();
  initAdminCharts();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', runDashboardInits);
} else {
  runDashboardInits();
}


// Patient Personal Progress Chart
async function initPatientDashboardChart() {
  const canvas = document.getElementById('patientProgressChart');
  if (!canvas) return;

  try {
    const resp = await fetch('/api/patient/progress');
    if (!resp.ok) return;
    const data = await resp.json();

    const labels = data.weekly_scores.map(d => `${d.day_name} (${d.date})`);
    const scores = data.weekly_scores.map(d => d.score);
    const accuracies = data.weekly_scores.map(d => d.accuracy);
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Cognitive Score',
            data: scores,
            borderColor: '#0d8269',
            backgroundColor: 'rgba(13, 130, 105, 0.15)',
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            pointRadius: 6,
            pointBackgroundColor: '#0d8269'
          },
          {
            label: 'Accuracy %',
            data: accuracies,
            borderColor: '#2b7a9e',
            borderDash: [5, 5],
            borderWidth: 2,
            fill: false,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#2b7a9e'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { font: { size: 14, weight: 'bold' } } },
          tooltip: {
            padding: 12,
            titleFont: { size: 14 },
            bodyFont: { size: 14 }
          }
        },
        scales: {
          y: {
            min: 40,
            max: 100,
            ticks: { font: { size: 13 } },
            grid: { color: '#e2e8f0' }
          },
          x: {
            ticks: { font: { size: 13 } },
            grid: { display: false }
          }
        }
      }
    });
  } catch (e) {
    console.warn("Could not load patient dashboard chart data:", e);
  }
}

// Caregiver Dashboard Charts (4 Comprehensive Visualizations)
async function initCaregiverCharts() {
  const trendCanvas = document.getElementById('caregiverTrendChart');
  const domainCanvas = document.getElementById('caregiverDomainChart');
  const activityCanvas = document.getElementById('caregiverActivityChart');
  const reminderCanvas = document.getElementById('caregiverReminderChart');

  if (!trendCanvas && !domainCanvas && !activityCanvas && !reminderCanvas) return;

  const patientId = trendCanvas ? trendCanvas.dataset.patientId : 1;

  try {
    const resp = await fetch(`/api/caregiver/patient/${patientId}/progress`);
    if (!resp.ok) return;
    const data = await resp.json();

    const labels = data.weekly_trend.map(d => d.label);
    const scores = data.weekly_trend.map(d => d.score);
    const accuracies = data.weekly_trend.map(d => d.accuracy);
    const activities = data.weekly_trend.map(d => d.activity_count);

    // 1. Cognitive Score Trend Line Chart
    if (trendCanvas) {
      const existingTrend = Chart.getChart(trendCanvas);
      if (existingTrend) existingTrend.destroy();
      new Chart(trendCanvas, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Cognitive Score',
            data: scores,
            borderColor: '#0d8269',
            backgroundColor: 'rgba(13, 130, 105, 0.12)',
            fill: true,
            tension: 0.3,
            borderWidth: 3,
            pointRadius: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { min: 40, max: 100 } }
        }
      });
    }

    // 2. Accuracy Trend Bar Chart
    if (domainCanvas) {
      const existingDomain = Chart.getChart(domainCanvas);
      if (existingDomain) existingDomain.destroy();
      new Chart(domainCanvas, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Game Accuracy %',
            data: accuracies,
            backgroundColor: '#2b7a9e',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { min: 40, max: 100 } }
        }
      });
    }

    // 3. Activity Frequency
    if (activityCanvas) {
      const existingActivity = Chart.getChart(activityCanvas);
      if (existingActivity) existingActivity.destroy();
      new Chart(activityCanvas, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Exercises Completed',
            data: activities,
            backgroundColor: '#10b981',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, stepSize: 1 } }
        }
      });
    }

    // 4. Reminder Completion Doughnut Chart
    if (reminderCanvas) {
      const existingReminder = Chart.getChart(reminderCanvas);
      if (existingReminder) existingReminder.destroy();
      const stats = data.reminder_stats || { completed: 8, missed: 1, pending: 2 };
      new Chart(reminderCanvas, {
        type: 'doughnut',
        data: {
          labels: ['Completed', 'Missed', 'Pending'],
          datasets: [{
            data: [stats.completed, stats.missed, stats.pending],
            backgroundColor: ['#198754', '#dc3545', '#ffc107'],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }

  } catch (e) {
    console.warn("Could not load caregiver chart data:", e);
  }
}

// Admin Dashboard Analytics
function initAdminCharts() {
  const regionalCanvas = document.getElementById('adminRegionalChart');
  const categoryCanvas = document.getElementById('adminCategoryChart');

  if (regionalCanvas) {
    const existingRegional = Chart.getChart(regionalCanvas);
    if (existingRegional) existingRegional.destroy();
    new Chart(regionalCanvas, {
      type: 'bar',
      data: {
        labels: ['Assam', 'Meghalaya', 'Sikkim', 'Manipur', 'Nagaland', 'Mizoram', 'Tripura'],
        datasets: [{
          label: 'Registered Patients',
          data: [1, 1, 1, 0, 0, 0, 0],
          backgroundColor: '#0d8269',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, stepSize: 1 } }
      }
    });
  }

  if (categoryCanvas) {
    const existingCategory = Chart.getChart(categoryCanvas);
    if (existingCategory) existingCategory.destroy();
    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Memory', 'Attention', 'Pattern', 'Daily Routine', 'Recognition', 'Emotion'],
        datasets: [{
          data: [6, 4, 3, 3, 2, 2],
          backgroundColor: ['#0d8269', '#2b7a9e', '#f59e0b', '#10b981', '#6366f1', '#ec4899']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }
}
