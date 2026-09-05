import SwiftUI

struct PrehistoryPage: View {
    let store: HistoryStore
    @State private var scale: PrehistoryScale = .origins
    @State private var age = PrehistoryScale.origins.initialAge
    @State private var selectedSiteID: String?
    @State private var showingSite = false
    @State private var showingSites = false
    @State private var showingDates = false
    @Environment(\.dynamicTypeSize) private var typeSize
    private var sites: [PrehistorySite] { store.content.prehistorySites ?? [] }
    private var visibleSites: [PrehistorySite] { sites.filter { $0.dating.includes(age, step: scale.step) } }
    private var positions: [Double] {
        Array(Set(sites.flatMap { [$0.dating.older, $0.dating.younger] }.filter { scale.younger <= $0 && $0 <= scale.older })).sorted(by: >)
    }
    private var previous: Double? { positions.last { $0 > age + 1 } }
    private var next: Double? { positions.first { $0 < age - 1 } }
    private func open(_ id: String) { selectedSiteID = id; showingSite = true }
    var body: some View {
        GeometryReader { geometry in
            ScrollView {
                VStack(spacing: 0) {
                    Picker("时间范围", selection: $scale) {
                        ForEach(PrehistoryScale.allCases) { item in Text(item.rawValue).tag(item) }
                    }.pickerStyle(.segmented).padding(.horizontal, 20).padding(.vertical, 12)
                        .accessibilityIdentifier("timeScale")
                    PrehistoryMap(sites: visibleSites, resetToken: scale.rawValue, openSite: open)
                        .frame(height: max(240, geometry.size.height - (typeSize.isAccessibilitySize ? 350 : 250)))
                        .accessibilityIdentifier("prehistoryTimeMap")
                    VStack(alignment: .leading, spacing: 14) {
                        HStack(alignment: .firstTextBaseline) {
                            Text(scale.label(age)).font(.system(.title2, design: .serif).weight(.medium))
                                .foregroundStyle(Theme.ink).accessibilityIdentifier("timelineDate")
                            Spacer(minLength: 8)
                            Button { showingDates = true } label: { Image(systemName: "info.circle").frame(width: 44, height: 44) }
                                .accessibilityLabel("年代说明")
                        }
                        Slider(value: Binding(get: { -age }, set: { age = -$0 }), in: scale.sliderRange, step: scale.step)
                            .tint(Theme.cinnabar).accessibilityLabel("历史时间轴")
                            .accessibilityValue(scale.label(age)).accessibilityIdentifier("historyTimeSlider")
                        HStack {
                            Text(scale.label(scale.older)); Spacer(); Text(scale.label(scale.younger))
                        }.font(.caption2).foregroundStyle(Theme.muted)
                        HStack {
                            Button("更早") { if let previous { age = previous } }.disabled(previous == nil)
                                .frame(minWidth: 44, minHeight: 44).accessibilityIdentifier("earlierTime")
                            Spacer()
                            Button { showingSites = true } label: {
                                Text(visibleSites.isEmpty ? "这一时期暂无收录" : "同时期遗址 \(visibleSites.count)处")
                                    .font(.subheadline.weight(.medium)).frame(minHeight: 44)
                            }.accessibilityIdentifier("contemporarySites")
                            Spacer()
                            Button("更晚") { if let next { age = next } }.disabled(next == nil)
                                .frame(minWidth: 44, minHeight: 44).accessibilityIdentifier("laterTime")
                        }
                    }.padding(.horizontal, 24).padding(.top, 8).padding(.bottom, 16)
                }
            }.scrollBounceBehavior(.basedOnSize)
        }
        .background(Theme.paper).tint(Theme.cinnabar)
        .navigationTitle("史前时间地图").navigationBarTitleDisplayMode(.inline)
        .toolbar { ToolbarItem(placement: .topBarTrailing) {
            NavigationLink("总览") { PrehistoryOverviewPage(store: store) }
        } }
        .onChange(of: scale) { _, value in age = value.initialAge }
        .navigationDestination(isPresented: $showingSite) {
            if let id = selectedSiteID { PrehistorySitePage(store: store, siteID: id) }
        }
        .sheet(isPresented: $showingSites) {
            NavigationStack {
                List {
                    Section(scale.label(age)) {
                        if visibleSites.isEmpty { Text("当前资料尚未覆盖这一时期，可拖动时间轴继续探索。").foregroundStyle(Theme.muted) }
                        ForEach(visibleSites) { site in
                            NavigationLink {
                                PrehistorySitePage(store: store, siteID: site.id)
                            } label: {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text(site.name).font(.headline)
                                    Text(site.dating.label).font(.caption).foregroundStyle(Theme.cinnabar)
                                    Text(site.summary).font(.subheadline).foregroundStyle(Theme.muted)
                                }.padding(.vertical, 6)
                            }.accessibilityIdentifier("contemporary_\(site.id)")
                        }
                    }
                }.navigationTitle("同时期遗址").navigationBarTitleDisplayMode(.inline)
                    .toolbar { ToolbarItem(placement: .confirmationAction) { Button("完成") { showingSites = false } } }
            }
        }
        .sheet(isPresented: $showingDates) {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        Text("年代是理解历史的坐标，也有测年与分期的不确定性。")
                        Text("地图按已收录遗址的约略年代筛选。同一时期出现，表示年代范围重叠，不代表彼此必然有交流。")
                        Text("只有约略测年点的遗址，在最接近的时间刻度显示；它不表示完整存续期。距今年代与公元前年代在轴上按1950年参照换算，原始年代写法保留在遗址卡片。")
                        Text("底图为现代地理参考；地图点位表示遗址，不表示文化的分布边界。暂时没有标记的时期，也不代表当时没有人类活动。")
                        Text("三个时间范围采用不同刻度，并有部分重叠，用于观察不同时间尺度，不作为统一的时代分界。")
                    }.font(.body).lineSpacing(6).padding(24)
                }.navigationTitle("年代说明").navigationBarTitleDisplayMode(.inline)
                    .toolbar { ToolbarItem(placement: .confirmationAction) { Button("完成") { showingDates = false } } }
            }.presentationDetents([.medium, .large])
        }
        .accessibilityIdentifier("prehistoryPage")
    }
}
