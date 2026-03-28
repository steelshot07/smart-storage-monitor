export function calculateStatus(device) {
  const issues = []

  if (device.temperature > 60) issues.push('critical temp')
  else if (device.temperature > 50) issues.push('high temp')

  if (device.lifespan < 30) issues.push('critical health')
  else if (device.lifespan < 60) issues.push('low health')

  const usedPercent = (device.usedGB / device.totalGB) * 100
  if (usedPercent > 95) issues.push('critical full')
  else if (usedPercent > 92) issues.push('almost full')

  if (device.riskPercent >= 70) issues.push('critical risk')
  else if (device.riskPercent >= 20) issues.push('high risk')

  if (issues.some(i => i.startsWith('critical'))) return 'danger'
  if (issues.length > 0) return 'warn'
  return 'good'
}

export function getHealthScore(device) {
  let score = 100

  score -= Math.max(0, device.temperature - 40) * 1.5
  score -= Math.max(0, 100 - device.lifespan)
  const usedPercent = (device.usedGB / device.totalGB) * 100
  score -= usedPercent > 90 ? 10 : 0

  return Math.max(0, Math.min(100, Math.round(score)))
}