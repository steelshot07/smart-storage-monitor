import './DeviceCard.css'
import RiskGauge from './RiskGauge'

function DeviceCard({ device }) {
    return (
        <div className="device-card">
            <div className="device-header">
                <span className="device-name">{device.name}</span>
                <span className={`health-badge ${device.status}`}>{device.status}</span>
            </div>
            <div className="device-metrics">
                <div className="metric">
                    <span className="metric-label">Temperature</span>
                    <span className="metric-value">{device.temperature}°C</span>
                </div>
                <div className="metric">
                    <span className="metric-label">Health</span>
                    <span className="metric-value">{device.health}%</span>
                </div>
                <div className="metric">
                    <span className="metric-label">Used</span>
                    <span className="metric-value">{device.usedGB} GB / {device.totalGB} GB</span>
                </div>

            </div>
            <div className="health-bar-container">
                <div
                    className="health-bar"
                    style={{
                        width: `${device.health}%`,
                        background: device.health > 70
                            ? 'var(--color-good)'
                            : device.health > 40
                                ? 'var(--color-warn)'
                                : 'var(--color-danger)'
                    }}
                />
            </div>
            <div className="prediction">
                <RiskGauge
                    riskPercent={device.riskPercent}
                    riskLabel={device.riskLabel}
                />
                <p className="prediction-message">{device.riskMessage}</p>
            </div>
        </div>
    )
}

export default DeviceCard