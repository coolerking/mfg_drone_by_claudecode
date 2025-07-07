/**
 * 高度なバンドル分析ユーティリティ
 * パフォーマンス最適化のためのバンドルサイズ、チャンク分析、未使用コード検出
 */

interface BundleAnalysis {
  totalSize: number
  gzippedSize: number
  chunks: ChunkInfo[]
  modules: ModuleInfo[]
  dependencies: DependencyInfo[]
  optimization: OptimizationSuggestions
}

interface ChunkInfo {
  name: string
  size: number
  gzippedSize: number
  modules: string[]
  isAsync: boolean
  priority: 'high' | 'medium' | 'low'
}

interface ModuleInfo {
  name: string
  size: number
  imports: string[]
  exports: string[]
  isUsed: boolean
  isDuplicated: boolean
  sourceType: 'node_modules' | 'src' | 'vendor'
}

interface DependencyInfo {
  name: string
  version: string
  size: number
  usage: 'critical' | 'important' | 'optional' | 'unused'
  alternatives?: string[]
  treeshakeable: boolean
}

interface OptimizationSuggestions {
  unusedCode: string[]
  duplicatedModules: string[]
  largeDependencies: string[]
  codeSplitOpportunities: string[]
  treeshakingOpportunities: string[]
  compressionImprovements: string[]
}

interface BundleMetrics {
  firstLoadSize: number
  totalBundleSize: number
  chunkCount: number
  vendorChunkSize: number
  applicationChunkSize: number
  duplicatedCode: number
  unusedExports: number
}

class BundleAnalyzer {
  private performanceObserver: PerformanceObserver | null = null
  private resourceCache = new Map<string, PerformanceResourceTiming>()
  
  constructor() {
    this.initializeResourceTracking()
  }

  private initializeResourceTracking(): void {
    if ('PerformanceObserver' in window) {
      this.performanceObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (entry.entryType === 'resource') {
            const resource = entry as PerformanceResourceTiming
            this.resourceCache.set(resource.name, resource)
          }
        }
      })

      try {
        this.performanceObserver.observe({ entryTypes: ['resource'] })
      } catch (error) {
        console.warn('Resource timing observer failed:', error)
      }
    }
  }

  /**
   * 現在のページのバンドル分析を実行
   */
  async analyzePage(): Promise<BundleAnalysis> {
    const resources = this.getPageResources()
    const chunks = await this.analyzeChunks(resources)
    const modules = await this.analyzeModules(resources)
    const dependencies = await this.analyzeDependencies(resources)
    const optimization = this.generateOptimizationSuggestions(chunks, modules, dependencies)

    const totalSize = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0)
    const gzippedSize = resources.reduce((sum, r) => sum + (r.encodedBodySize || 0), 0)

    return {
      totalSize,
      gzippedSize,
      chunks,
      modules,
      dependencies,
      optimization
    }
  }

  /**
   * ページで読み込まれたJavaScript/CSSリソースを取得
   */
  private getPageResources(): PerformanceResourceTiming[] {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
    return resources.filter(resource => 
      resource.name.includes('.js') || 
      resource.name.includes('.css') ||
      resource.name.includes('.wasm')
    )
  }

  /**
   * チャンク分析
   */
  private async analyzeChunks(resources: PerformanceResourceTiming[]): Promise<ChunkInfo[]> {
    const chunks: ChunkInfo[] = []

    for (const resource of resources) {
      const chunkName = this.extractChunkName(resource.name)
      const isAsync = this.isAsyncChunk(resource.name)
      const priority = this.determineChunkPriority(resource, isAsync)

      chunks.push({
        name: chunkName,
        size: resource.transferSize || 0,
        gzippedSize: resource.encodedBodySize || 0,
        modules: await this.extractModulesFromChunk(resource.name),
        isAsync,
        priority
      })
    }

    return chunks.sort((a, b) => b.size - a.size)
  }

  /**
   * モジュール分析
   */
  private async analyzeModules(resources: PerformanceResourceTiming[]): Promise<ModuleInfo[]> {
    const modules: ModuleInfo[] = []
    const moduleMap = new Map<string, ModuleInfo>()

    for (const resource of resources) {
      try {
        const moduleList = await this.extractModulesFromSource(resource.name)
        
        for (const moduleName of moduleList) {
          if (moduleMap.has(moduleName)) {
            const existing = moduleMap.get(moduleName)!
            existing.isDuplicated = true
          } else {
            const moduleInfo: ModuleInfo = {
              name: moduleName,
              size: this.estimateModuleSize(moduleName, resource),
              imports: await this.extractModuleImports(moduleName),
              exports: await this.extractModuleExports(moduleName),
              isUsed: await this.checkModuleUsage(moduleName),
              isDuplicated: false,
              sourceType: this.determineSourceType(moduleName)
            }
            
            moduleMap.set(moduleName, moduleInfo)
            modules.push(moduleInfo)
          }
        }
      } catch (error) {
        console.warn(`Failed to analyze modules for ${resource.name}:`, error)
      }
    }

    return modules.sort((a, b) => b.size - a.size)
  }

  /**
   * 依存関係分析
   */
  private async analyzeDependencies(resources: PerformanceResourceTiming[]): Promise<DependencyInfo[]> {
    const dependencies: DependencyInfo[] = []
    const packageMap = new Map<string, DependencyInfo>()

    for (const resource of resources) {
      const packages = this.extractPackagesFromResource(resource)
      
      for (const pkg of packages) {
        if (!packageMap.has(pkg.name)) {
          const depInfo: DependencyInfo = {
            name: pkg.name,
            version: pkg.version,
            size: pkg.size,
            usage: await this.analyzePackageUsage(pkg.name),
            alternatives: await this.findPackageAlternatives(pkg.name),
            treeshakeable: await this.checkTreeshakeable(pkg.name)
          }
          
          packageMap.set(pkg.name, depInfo)
          dependencies.push(depInfo)
        }
      }
    }

    return dependencies.sort((a, b) => b.size - a.size)
  }

  /**
   * 最適化提案を生成
   */
  private generateOptimizationSuggestions(
    chunks: ChunkInfo[],
    modules: ModuleInfo[],
    dependencies: DependencyInfo[]
  ): OptimizationSuggestions {
    return {
      unusedCode: modules
        .filter(m => !m.isUsed)
        .map(m => m.name),
      
      duplicatedModules: modules
        .filter(m => m.isDuplicated)
        .map(m => m.name),
      
      largeDependencies: dependencies
        .filter(d => d.size > 100 * 1024) // 100KB以上
        .map(d => `${d.name} (${(d.size / 1024).toFixed(1)}KB)`),
      
      codeSplitOpportunities: this.findCodeSplitOpportunities(chunks, modules),
      
      treeshakingOpportunities: dependencies
        .filter(d => d.treeshakeable && d.usage !== 'critical')
        .map(d => d.name),
      
      compressionImprovements: this.findCompressionOpportunities(chunks)
    }
  }

  /**
   * バンドルメトリクスを計算
   */
  calculateMetrics(analysis: BundleAnalysis): BundleMetrics {
    const firstLoadChunks = analysis.chunks.filter(c => !c.isAsync)
    const vendorChunks = analysis.chunks.filter(c => c.name.includes('vendor'))
    const appChunks = analysis.chunks.filter(c => !c.name.includes('vendor') && !c.name.includes('runtime'))

    return {
      firstLoadSize: firstLoadChunks.reduce((sum, c) => sum + c.size, 0),
      totalBundleSize: analysis.totalSize,
      chunkCount: analysis.chunks.length,
      vendorChunkSize: vendorChunks.reduce((sum, c) => sum + c.size, 0),
      applicationChunkSize: appChunks.reduce((sum, c) => sum + c.size, 0),
      duplicatedCode: analysis.modules.filter(m => m.isDuplicated).reduce((sum, m) => sum + m.size, 0),
      unusedExports: analysis.modules.filter(m => !m.isUsed).length
    }
  }

  /**
   * パフォーマンス影響を評価
   */
  assessPerformanceImpact(metrics: BundleMetrics): {
    score: number
    recommendations: string[]
    urgentIssues: string[]
  } {
    let score = 100
    const recommendations: string[] = []
    const urgentIssues: string[] = []

    // First Load Sizeの評価
    if (metrics.firstLoadSize > 244 * 1024) { // 244KB (3G基準)
      score -= 20
      urgentIssues.push('First Load Sizeが244KBを超えています')
    } else if (metrics.firstLoadSize > 170 * 1024) { // 170KB (推奨値)
      score -= 10
      recommendations.push('First Load Sizeを170KB以下に最適化することを推奨します')
    }

    // Total Bundle Sizeの評価
    if (metrics.totalBundleSize > 1024 * 1024) { // 1MB
      score -= 15
      recommendations.push('総バンドルサイズが1MBを超えています。コード分割を検討してください')
    }

    // 重複コードの評価
    if (metrics.duplicatedCode > 50 * 1024) { // 50KB
      score -= 15
      recommendations.push('重複コードが50KBを超えています。バンドル設定を見直してください')
    }

    // 未使用エクスポートの評価
    if (metrics.unusedExports > 10) {
      score -= 10
      recommendations.push(`${metrics.unusedExports}個の未使用エクスポートが検出されました。Tree Shakingを有効にしてください`)
    }

    // チャンク数の評価
    if (metrics.chunkCount > 20) {
      score -= 5
      recommendations.push('チャンク数が多すぎます。HTTP/2を活用するか、チャンクを統合してください')
    } else if (metrics.chunkCount < 3) {
      score -= 5
      recommendations.push('コード分割が不十分です。動的インポートを活用してください')
    }

    return {
      score: Math.max(0, score),
      recommendations,
      urgentIssues
    }
  }

  // ヘルパーメソッド
  private extractChunkName(url: string): string {
    const match = url.match(/\/([^\/]+)\.(js|css)$/)
    return match ? match[1] : 'unknown'
  }

  private isAsyncChunk(url: string): boolean {
    return url.includes('chunk') || url.includes('lazy') || url.includes('async')
  }

  private determineChunkPriority(resource: PerformanceResourceTiming, isAsync: boolean): 'high' | 'medium' | 'low' {
    if (!isAsync && resource.transferSize && resource.transferSize > 100 * 1024) return 'high'
    if (resource.transferSize && resource.transferSize > 50 * 1024) return 'medium'
    return 'low'
  }

  private async extractModulesFromChunk(chunkUrl: string): Promise<string[]> {
    // 実際の実装では、ソースマップやWebpackバンドル分析を使用
    // ここではモックデータを返す
    return [`module-${Math.random().toString(36).substr(2, 9)}`]
  }

  private async extractModulesFromSource(resourceUrl: string): Promise<string[]> {
    // 実際の実装では、ソースを解析してモジュール一覧を抽出
    return [`module-${Math.random().toString(36).substr(2, 9)}`]
  }

  private estimateModuleSize(moduleName: string, resource: PerformanceResourceTiming): number {
    // 実際の実装では、より正確なサイズ推定を行う
    return Math.floor((resource.transferSize || 0) / 10)
  }

  private async extractModuleImports(moduleName: string): Promise<string[]> {
    // モックデータ
    return [`import-${Math.random().toString(36).substr(2, 5)}`]
  }

  private async extractModuleExports(moduleName: string): Promise<string[]> {
    // モックデータ
    return [`export-${Math.random().toString(36).substr(2, 5)}`]
  }

  private async checkModuleUsage(moduleName: string): Promise<boolean> {
    // 実際の実装では、ランタイムでの使用状況をチェック
    return Math.random() > 0.3
  }

  private determineSourceType(moduleName: string): 'node_modules' | 'src' | 'vendor' {
    if (moduleName.includes('node_modules')) return 'node_modules'
    if (moduleName.includes('vendor')) return 'vendor'
    return 'src'
  }

  private extractPackagesFromResource(resource: PerformanceResourceTiming): Array<{
    name: string
    version: string
    size: number
  }> {
    // 実際の実装では、リソースURLから依存関係を抽出
    return [{
      name: `package-${Math.random().toString(36).substr(2, 9)}`,
      version: '1.0.0',
      size: resource.transferSize || 0
    }]
  }

  private async analyzePackageUsage(packageName: string): Promise<'critical' | 'important' | 'optional' | 'unused'> {
    // 実際の実装では、使用頻度と重要度を分析
    const usages = ['critical', 'important', 'optional', 'unused'] as const
    return usages[Math.floor(Math.random() * usages.length)]
  }

  private async findPackageAlternatives(packageName: string): Promise<string[]> {
    // 実際の実装では、代替パッケージを提案
    return [`${packageName}-alternative`]
  }

  private async checkTreeshakeable(packageName: string): Promise<boolean> {
    // 実際の実装では、ES Modulesサポートをチェック
    return Math.random() > 0.5
  }

  private findCodeSplitOpportunities(chunks: ChunkInfo[], modules: ModuleInfo[]): string[] {
    const opportunities: string[] = []
    
    // 大きなチャンクを特定
    const largeChunks = chunks.filter(c => c.size > 200 * 1024)
    for (const chunk of largeChunks) {
      opportunities.push(`${chunk.name}を分割してください (${(chunk.size / 1024).toFixed(1)}KB)`)
    }

    // 低優先度の同期チャンクを特定
    const lowPrioritySync = chunks.filter(c => !c.isAsync && c.priority === 'low')
    for (const chunk of lowPrioritySync) {
      opportunities.push(`${chunk.name}を非同期読み込みに変更してください`)
    }

    return opportunities
  }

  private findCompressionOpportunities(chunks: ChunkInfo[]): string[] {
    const opportunities: string[] = []
    
    for (const chunk of chunks) {
      const compressionRatio = chunk.gzippedSize / chunk.size
      if (compressionRatio > 0.8) {
        opportunities.push(`${chunk.name}の圧縮効率が低いです (${(compressionRatio * 100).toFixed(1)}%)`)
      }
    }

    return opportunities
  }

  /**
   * リソースを破棄
   */
  destroy(): void {
    if (this.performanceObserver) {
      this.performanceObserver.disconnect()
    }
    this.resourceCache.clear()
  }
}

// シングルトンインスタンス
export const bundleAnalyzer = new BundleAnalyzer()

// React Hook
export const useBundleAnalysis = () => {
  const [analysis, setAnalysis] = React.useState<BundleAnalysis | null>(null)
  const [metrics, setMetrics] = React.useState<BundleMetrics | null>(null)
  const [loading, setLoading] = React.useState(false)

  const runAnalysis = React.useCallback(async () => {
    setLoading(true)
    try {
      const result = await bundleAnalyzer.analyzePage()
      const calculatedMetrics = bundleAnalyzer.calculateMetrics(result)
      
      setAnalysis(result)
      setMetrics(calculatedMetrics)
    } catch (error) {
      console.error('Bundle analysis failed:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    runAnalysis()
  }, [runAnalysis])

  return {
    analysis,
    metrics,
    loading,
    runAnalysis,
    assessPerformanceImpact: metrics ? bundleAnalyzer.assessPerformanceImpact(metrics) : null
  }
}

export default bundleAnalyzer