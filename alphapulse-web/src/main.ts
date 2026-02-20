import './style.css'
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

// Global chart instance to handle updates
let predictionChart: Chart | null = null;

// Subtle Scroll Revelations
document.addEventListener('DOMContentLoaded', () => {
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    const sections = document.querySelectorAll('.section, .hero');
    sections.forEach(section => {
        section.classList.add('reveal');
        observer.observe(section);
    });

    // Prediction Form Logic
    const form = document.getElementById('prediction-form') as HTMLFormElement;
    const tickerInput = document.getElementById('ticker-input') as HTMLInputElement;
    const resultDiv = document.getElementById('prediction-result');
    const loader = document.getElementById('loader');

    const resTicker = document.getElementById('res-ticker');
    const resPrice = document.getElementById('res-price');
    const resDirection = document.getElementById('res-direction');
    const resConf = document.getElementById('res-conf');
    const resAccuracy = document.getElementById('res-accuracy');
    const chartCanvas = document.getElementById('prediction-chart') as HTMLCanvasElement;

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) return;

        // UI State: Loading
        resultDiv?.classList.add('hidden');
        loader?.classList.remove('hidden');

        try {
            const response = await fetch(`http://localhost:8000/predict/${ticker}`);
            if (!response.ok) throw new Error('Prediction failed');

            const data = await response.json();

            // Update UI with results
            if (resTicker) resTicker.innerText = data.ticker;
            if (resPrice) resPrice.innerText = `$${data.last_price}`;
            if (resDirection) {
                resDirection.innerText = data.direction;
                resDirection.className = `prediction-badge ${data.direction.toLowerCase()}`;
            }
            if (resConf) resConf.innerText = `${data.confidence}%`;
            if (resAccuracy) resAccuracy.innerText = `${data.accuracy}%`;

            // Handle Chart Rendering
            if (chartCanvas && data.history) {
                if (predictionChart) {
                    predictionChart.destroy();
                }

                const labels = data.history.map((h: any) => h.date);
                const prices = data.history.map((h: any) => h.price);
                const isUp = data.direction === "UP";
                const chartColor = isUp ? '#2D5A27' : '#A63D40'; // Match CSS variables

                predictionChart = new Chart(chartCanvas, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Closing Price',
                            data: prices,
                            borderColor: chartColor,
                            backgroundColor: chartColor + '20', // Add transparency
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0,
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: {
                                display: false // Hide x-axis for cleaner look
                            },
                            y: {
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.05)'
                                },
                                ticks: {
                                    color: 'rgba(255, 255, 255, 0.5)',
                                    font: { size: 10 }
                                }
                            }
                        }
                    }
                });
            }

            loader?.classList.add('hidden');
            resultDiv?.classList.remove('hidden');
        } catch (error) {
            console.error(error);
            alert("Error: Predictive analysis failed. Please check the ticker and try again.");
            loader?.classList.add('hidden');
        }
    });
});

// Implementation of reveal effect
const style = document.createElement('style');
style.innerHTML = `
    .reveal {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.8s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    .reveal.visible {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(style);
