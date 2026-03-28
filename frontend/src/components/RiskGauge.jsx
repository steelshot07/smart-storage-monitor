import { useEffect, useRef } from 'react'
import './RiskGauge.css'

function RiskGauge({ riskPercent, riskLabel }) {
    const needleRef = useRef(null)
    const arcRef = useRef(null)

    const color = riskPercent >= 70 ? '#ef4444'
        : riskPercent >= 40 ? '#f59e0b'
            : '#22c55e'

    useEffect(() => {
        // needle goes from -180deg (0%) to 0deg (100%)
        const angle = -180 + (riskPercent / 100) * 180

        // arc dash animation
        const totalLength = 377
        const filled = (riskPercent / 100) * totalLength
        const offset = totalLength - filled

        if (needleRef.current) {
            needleRef.current.style.transform = `rotate(${angle}deg)`
        }
        if (arcRef.current) {
            arcRef.current.style.strokeDashoffset = offset
        }
    }, [riskPercent])

    return (
        <div className="gauge-wrapper">
            <svg viewBox="0 0 300 170" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#22c55e" />
                        <stop offset="50%" stopColor="#f59e0b" />
                        <stop offset="100%" stopColor="#ef4444" />
                    </linearGradient>
                </defs>

                {/* background track */}
                <path
                    d="M 30 150 A 120 120 0 0 1 270 150"
                    fill="none" stroke="#2d3148"
                    strokeWidth="16" strokeLinecap="round"
                />

                {/* dim full arc */}
                <path
                    d="M 30 150 A 120 120 0 0 1 270 150"
                    fill="none" stroke="url(#gaugeGrad)"
                    strokeWidth="16" strokeLinecap="round"
                    opacity="0.2"
                />

                {/* animated filled arc */}
                <path
                    ref={arcRef}
                    d="M 30 150 A 120 120 0 0 1 270 150"
                    fill="none" stroke="url(#gaugeGrad)"
                    strokeWidth="16" strokeLinecap="round"
                    strokeDasharray="377"
                    strokeDashoffset="377"
                    style={{ transition: 'stroke-dashoffset 1.2s ease-out' }}
                />



                {/* risk value */}
                <text x="150" y="105" fontSize="26" fontWeight="600" fill={color} fontFamily="system-ui" textAnchor="middle">
                    {riskPercent}%
                </text>
                <text x="150" y="125" fontSize="11" fill="#64748b" fontFamily="system-ui" textAnchor="middle">
                    failure risk
                </text>
            </svg>

            <p className="gauge-label" style={{ color }}>{riskLabel}</p>
        </div>
    )
}

export default RiskGauge