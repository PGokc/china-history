import Foundation
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
    private var guideGroups: [(title: String, note: String, ids: [String])] {
        [
            ("远古人类", "从最早活动线索到现代人扩散", ["shangchen", "nihewan", "yuanmou", "lantian", "zhoukoudian", "dingcun", "jinniushan", "tianyuan", "shandingdong"]),
            ("定居与农业", "陶器、稻粟栽培与村落生活", ["xianrendong", "shangshan", "jiahu", "hemudu", "banpo", "chengtoushan"]),
            ("复杂聚落", "区域中心、城址与早期国家线索", ["dawenkou", "niuheliang", "liangzhu", "majiayao", "taosi", "shimao"]),
        ]
    }
    private func open(_ id: String) { selectedSiteID = id; showingSite = true }
    var body: some View {
        GeometryReader { geometry in
            ScrollView {
                VStack(spacing: 0) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("约210万年前—约前2070")
                            .font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                        Text("在时间中观察遗址")
                            .font(.system(.title2, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                        Text("拖动年代，地图只保留与当前时间重叠的地点。")
                            .font(.subheadline).foregroundStyle(Theme.muted)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 24).padding(.top, 18).padding(.bottom, 8)
                    Picker("时间范围", selection: $scale) {
                        ForEach(PrehistoryScale.allCases) { item in Text(item.rawValue).tag(item) }
                    }.pickerStyle(.segmented).padding(.horizontal, 20).padding(.vertical, 12)
                        .accessibilityIdentifier("timeScale")
                    PrehistoryMap(sites: visibleSites, resetToken: scale.rawValue, openSite: open)
                        .frame(height: typeSize.isAccessibilitySize ? 310 : max(360, geometry.size.height * 0.56))
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
                    }.padding(.horizontal, 24).padding(.top, 10).padding(.bottom, 30)

                    VStack(alignment: .leading, spacing: 34) {
                        if let profile = store.dynastyProfile("prehistory") {
                            NavigationLink {
                                PrehistoryInterpretationPage(store: store, profile: profile)
                            } label: {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("理解史前中国")
                                        .font(.system(.title2, design: .serif).weight(.medium))
                                        .foregroundStyle(Theme.ink)
                                    Text("从人类演化、农业形成与区域社会读懂考古证据")
                                        .font(.subheadline).foregroundStyle(Theme.text).lineSpacing(4)
                                    Text("五个问题 · 一篇宏观导读")
                                        .font(.caption).foregroundStyle(Theme.cinnabar)
                                }
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.vertical, 19)
                                .overlay(alignment: .top) { Rectangle().fill(Theme.line.opacity(0.55)).frame(height: 0.5) }
                                .overlay(alignment: .bottom) { Rectangle().fill(Theme.line.opacity(0.55)).frame(height: 0.5) }
                                .contentShape(Rectangle())
                            }
                            .buttonStyle(.plain)
                            .accessibilityIdentifier("prehistoryInterpretationEntry")
                        }
                        VStack(alignment: .leading, spacing: 7) {
                            Text("遗址导览")
                                .font(.system(.title2, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                                .accessibilityIdentifier("prehistorySiteGuide")
                            Text("21处遗址按历史问题分成三段；地图负责比较时间与位置，列表负责进入详细阅读。")
                                .font(.subheadline).foregroundStyle(Theme.muted).lineSpacing(4)
                        }
                        ForEach(Array(guideGroups.enumerated()), id: \.offset) { _, group in
                            PrehistoryGuideSection(store: store, title: group.title, note: group.note, ids: group.ids)
                        }
                    }
                    .padding(.horizontal, 24).padding(.bottom, Theme.pageBottom)
                }
            }.scrollBounceBehavior(.basedOnSize)
        }
        .background(Theme.paper).tint(Theme.cinnabar)
        .navigationTitle("史前中国").navigationBarTitleDisplayMode(.inline)
        .onChange(of: scale) { _, value in age = value.initialAge }
        .navigationDestination(isPresented: $showingSite) {
            if let id = selectedSiteID { PrehistorySitePage(store: store, siteID: id) }
        }
        .sheet(isPresented: $showingSites) {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        Text(scale.label(age)).font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                            .padding(.bottom, 12)
                        if visibleSites.isEmpty {
                            Text("当前资料尚未覆盖这一时期，可拖动时间轴继续探索。")
                                .foregroundStyle(Theme.muted).padding(.vertical, 28)
                        }
                        ForEach(Array(visibleSites.enumerated()), id: \.element.id) { index, site in
                            NavigationLink {
                                PrehistorySitePage(store: store, siteID: site.id)
                            } label: {
                                PrehistorySiteEditorialRow(site: site, index: index + 1, showsSummary: true)
                            }
                            .buttonStyle(.plain).accessibilityIdentifier("contemporary_\(site.id)")
                        }
                    }.padding(.horizontal, 24).padding(.top, 20).padding(.bottom, 36)
                }
                .background(Theme.paper)
                .navigationTitle("同时期遗址").navigationBarTitleDisplayMode(.inline)
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

private struct PrehistoryInterpretationPage: View {
    let store: HistoryStore
    let profile: DynastyProfile

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 28) {
                VStack(alignment: .leading, spacing: 9) {
                    Text("宏观导读")
                        .font(.caption.weight(.medium)).foregroundStyle(Theme.cinnabar)
                    Text("理解史前中国")
                        .font(.system(size: 36, weight: .medium, design: .serif)).foregroundStyle(Theme.ink)
                    Text(profile.subtitle)
                        .font(.title3).foregroundStyle(Theme.text).lineSpacing(4)
                }

                DynastyOverviewBlock(title: "从证据开始", text: profile.overview)

                VStack(alignment: .leading, spacing: 0) {
                    Text("五个关键问题")
                        .font(.system(.title3, design: .serif).weight(.medium))
                        .foregroundStyle(Theme.ink).padding(.bottom, 3)
                    ForEach(profile.sections) { section in
                        VStack(alignment: .leading, spacing: 10) {
                            Text(section.title)
                                .font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                            Text(section.text)
                                .font(.body).foregroundStyle(Theme.text).lineSpacing(6)
                        }
                        .padding(.vertical, 19)
                        .accessibilityIdentifier("prehistoryInterpretation_\(section.id)")
                        if section.id != profile.sections.last?.id {
                            Divider().overlay(Theme.line.opacity(0.55))
                        }
                    }
                }
                SourcesView(store: store, ids: profile.sources)
            }
            .padding(.horizontal, 24).padding(.top, 22).padding(.bottom, Theme.pageBottom)
        }
        .background(Theme.paper)
        .navigationTitle("理解史前中国")
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(Theme.paper, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
        .accessibilityIdentifier("prehistoryInterpretationPage")
    }
}

private struct PrehistoryGuideSection: View {
    let store: HistoryStore
    let title: String
    let note: String
    let ids: [String]

    private var sites: [PrehistorySite] { ids.compactMap { store.prehistorySite($0) } }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(title).font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
            Text(note).font(.caption).foregroundStyle(Theme.muted).padding(.top, 4).padding(.bottom, 10)
            ForEach(Array(sites.enumerated()), id: \.element.id) { index, site in
                NavigationLink(value: DetailRoute.prehistorySite(site.id)) {
                    PrehistorySiteEditorialRow(site: site, index: index + 1, showsSummary: false)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("prehistoricGuide_\(site.id)")
            }
        }
    }
}

private struct PrehistorySiteEditorialRow: View {
    let site: PrehistorySite
    let index: Int
    let showsSummary: Bool

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Text(String(format: "%02d", index))
                .font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                .frame(width: 26, alignment: .leading).padding(.top, 3)
            VStack(alignment: .leading, spacing: 5) {
                Text(site.name).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(site.period).font(.caption.monospacedDigit()).foregroundStyle(Theme.muted)
                Text(site.location).font(.caption).foregroundStyle(Theme.muted)
                if showsSummary {
                    Text(site.summary).font(.subheadline).foregroundStyle(Theme.text).lineSpacing(4)
                        .padding(.top, 2)
                }
            }
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 13).contentShape(Rectangle())
    }
}
