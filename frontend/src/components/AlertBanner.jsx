import './AlertBanner.css'

function AlertBanner({devices}) {
    const problems = devices.filter(d => d.status === 'warn' || d.status === 'danger')

    if(problems.length === 0) return null

    return(
        <div className="alert-banner">
            <span className="alert-icon">⚠</span>
            <span className="alert-message">{problems.map(d => d.name).join(', ')} {problems.length === 1 ? 'needs' : 'need'} attention</span>
        </div>
    )
}


export default AlertBanner