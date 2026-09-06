import SwiftUI
import MapKit

struct DynastyDetailPage: View {
    let store: HistoryStore
    let dynastyID: String

    var body: some View {
        if dynastyID == "prehistory" {
            PrehistoryPage(store: store)
        } else if let dynasty = store.dynasty(dynastyID), let profile = store.dynastyProfile(dynastyID) {
            ScrollView {
                VStack(alignment: .leading, spacing: 28) {
                    VStack(alignment: .leading, spacing: 9) {
                        Text(dynasty.years).font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                        Text(dynasty.name).font(.system(size: 39, weight: .medium, design: .serif)).foregroundStyle(Theme.ink)
                        Text(profile.subtitle).font(.title3).foregroundStyle(Theme.text).lineSpacing(4)
                    }
                    DynastyOverviewBlock(title: "朝代总览", text: profile.overview)
                    if let map = store.territoryMap(dynastyID) {
                        TerritoryMapCard(store: store, map: map)
                    }
                    if dynastyID == "zhou", let guide = store.zhouGuide {
                        ZhouTopicShelf(guide: guide)
                    }
                    VStack(alignment: .leading, spacing: 0) {
                        Text("理解这个时代").font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink).padding(.bottom, 3)
                        ForEach(profile.sections) { section in
                            VStack(alignment: .leading, spacing: 9) {
                                Text(section.title).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                                Text(section.text).font(.body).foregroundStyle(Theme.text).lineSpacing(6)
                            }.padding(.vertical, 18)
                            if section.id != profile.sections.last?.id { Divider().overlay(Theme.line.opacity(0.55)) }
                        }
                    }
                    SourcesView(store: store, ids: profile.sources)
                }.padding(.horizontal, 24).padding(.top, 22).padding(.bottom, 24)
            }
            .background(Theme.paper)
            .navigationTitle(dynasty.name + "概览")
            .navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .accessibilityIdentifier("dynastyDetail_\(dynastyID)")
        } else {
            ContentUnavailableView("尚无朝代介绍", systemImage: "book.closed")
        }
    }
}

private struct ZhouTopicShelf: View {
    let guide: EraGuide
    private let groups = ["思想", "诸侯", "变法"]

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 7) {
                Text(guide.title).font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                Text(guide.subtitle).font(.subheadline).foregroundStyle(Theme.muted).lineSpacing(4)
            }
            ForEach(groups, id: \.self) { group in
                let topics = guide.topics.filter { $0.category == group }
                if !topics.isEmpty {
                    VStack(alignment: .leading, spacing: 0) {
                        Text(group).font(.caption.weight(.medium)).foregroundStyle(Theme.cinnabar).padding(.bottom, 4)
                        ForEach(topics) { topic in
                            NavigationLink(value: DetailRoute.eraTopic(topic.id)) {
                                VStack(alignment: .leading, spacing: 6) {
                                    HStack(alignment: .firstTextBaseline) {
                                        Text(topic.name).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                                        Spacer()
                                        Text(topic.years).font(.caption.monospacedDigit()).foregroundStyle(Theme.muted)
                                    }
                                    Text(topic.call).font(.caption).foregroundStyle(Theme.cinnabar)
                                    Text(topic.summary).font(.subheadline).foregroundStyle(Theme.text).lineLimit(2).lineSpacing(4)
                                }
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.vertical, 15)
                                .contentShape(Rectangle())
                            }
                            .buttonStyle(QuietRowStyle())
                            .accessibilityIdentifier("zhouTopic_\(topic.id)")
                            if topic.id != topics.last?.id { Divider().overlay(Theme.line.opacity(0.45)) }
                        }
                    }
                }
            }
        }
        .accessibilityElement(children: .contain)
    }
}

struct EraTopicPage: View {
    let store: HistoryStore
    let topicID: String

    var body: some View {
        if let topic = store.eraTopic(topicID) {
            ScrollView {
                VStack(alignment: .leading, spacing: 26) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(topic.category).font(.caption.weight(.medium)).foregroundStyle(Theme.cinnabar)
                        Text(topic.name).font(.system(size: 38, weight: .medium, design: .serif)).foregroundStyle(Theme.ink)
                        Text(topic.call).font(.title3).foregroundStyle(Theme.text)
                        Text(topic.years).font(.caption.monospacedDigit()).foregroundStyle(Theme.muted)
                    }
                    Text(topic.summary).font(.body).foregroundStyle(Theme.text).lineSpacing(7)
                    VStack(alignment: .leading, spacing: 0) {
                        ForEach(topic.sections) { section in
                            VStack(alignment: .leading, spacing: 10) {
                                Text(section.title).font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                                Text(section.text).font(.body).foregroundStyle(Theme.text).lineSpacing(7).fixedSize(horizontal: false, vertical: true)
                            }.padding(.vertical, 17)
                            if section.id != topic.sections.last?.id { Divider().overlay(Theme.line.opacity(0.5)) }
                        }
                    }
                    VStack(alignment: .leading, spacing: 10) {
                        Text("资料依据").font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                        ForEach(topic.sources) { source in
                            if let url = URL(string: source.url) {
                                Link(source.title, destination: url)
                                    .font(.caption).foregroundStyle(Theme.cinnabar).frame(minHeight: 36, alignment: .leading)
                            }
                        }
                    }
                }.padding(.horizontal, 24).padding(.top, 22).padding(.bottom, 70)
            }
            .background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle(topic.name).navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .accessibilityIdentifier("eraTopic_\(topic.id)")
        } else {
            ContentUnavailableView("人物资料未能载入", systemImage: "book.closed")
        }
    }
}

private struct DynastyOverviewBlock: View {
    let title, text: String
    private var paragraphs: [String] { text.components(separatedBy: "\n\n").filter { !$0.isEmpty } }
    var body: some View {
        VStack(alignment: .leading, spacing: 13) {
            Text(title).font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
            ForEach(Array(paragraphs.enumerated()), id: \.offset) { _, paragraph in
                Text(paragraph).font(.body).foregroundStyle(Theme.text).lineSpacing(7).fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

struct TerritoryMapCard: View {
    let store: HistoryStore
    let map: TerritoryMap

    private func color(_ tone: String) -> Color {
        switch tone {
        case "red": return Theme.cinnabar
        case "ochre": return Color(red: 157/255, green: 117/255, blue: 62/255)
        case "slate": return Color(red: 91/255, green: 105/255, blue: 112/255)
        default: return Theme.ink
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text("疆域与格局").font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                Spacer()
                Text(map.date).font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
            }
            Map(initialPosition: .region(MKCoordinateRegion(
                center: CLLocationCoordinate2D(latitude: map.centerLatitude, longitude: map.centerLongitude),
                span: MKCoordinateSpan(latitudeDelta: map.latitudeDelta, longitudeDelta: map.longitudeDelta)
            )), interactionModes: []) {
                ForEach(map.regions) { region in
                    MapPolygon(coordinates: region.points.map { CLLocationCoordinate2D(latitude: $0.latitude, longitude: $0.longitude) })
                        .foregroundStyle(color(region.tone).opacity(0.30))
                        .stroke(color(region.tone), lineWidth: 1.4)
                    Annotation("", coordinate: CLLocationCoordinate2D(latitude: region.labelLatitude, longitude: region.labelLongitude)) {
                        Text(region.name).font(.caption2.weight(.semibold)).foregroundStyle(color(region.tone))
                            .padding(.horizontal, 6).padding(.vertical, 3).background(Theme.paper.opacity(0.90), in: Capsule())
                    }
                }
            }
            .mapStyle(.standard(elevation: .flat, pointsOfInterest: .excludingAll, showsTraffic: false))
            .frame(height: 260)
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .accessibilityIdentifier("territoryMap_\(map.id)")
            Text(map.caption).font(.caption).foregroundStyle(Theme.muted).lineSpacing(4)
            if map.regions.count > 1 {
                HStack(spacing: 14) {
                    ForEach(map.regions) { region in
                        HStack(spacing: 5) { Circle().fill(color(region.tone)).frame(width: 7, height: 7); Text(region.name) }
                    }
                }.font(.caption2).foregroundStyle(Theme.muted)
            }
            DisclosureGroup("地图依据") {
                SourcesView(store: store, ids: map.sources, compact: true).padding(.top, 8)
            }.font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

struct PrehistoryOverviewPage: View {
    let store: HistoryStore
    @State private var selectedSiteID: String?
    @State private var showingSite = false
    private var sites: [PrehistorySite] { store.content.prehistorySites ?? [] }
    private var profile: DynastyProfile? { store.dynastyProfile("prehistory") }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 28) {
                VStack(alignment: .leading, spacing: 9) {
                    Text("约210万年前—约前2070").font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                    Text("史前中国").font(.system(size: 38, weight: .medium, design: .serif)).foregroundStyle(Theme.ink)
                    Text(profile?.subtitle ?? "从遗址读懂没有文字的历史").font(.title3).foregroundStyle(Theme.text)
                }
                if let overview = profile?.overview { DynastyOverviewBlock(title: "时代总览", text: overview) }

                VStack(alignment: .leading, spacing: 12) {
                    Text("遗址分布").font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                    PrehistoryMap(sites: sites) { id in
                        selectedSiteID = id
                        showingSite = true
                    }
                    .frame(height: 390)
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .accessibilityIdentifier("prehistoryMap")
                    Text("点按名称查看遗址，点按分组展开相邻地点。")
                        .font(.caption).foregroundStyle(Theme.muted).lineSpacing(4)

                }

                VStack(alignment: .leading, spacing: 0) {
                    Text("沿年代浏览").font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink).padding(.bottom, 8)
                    ForEach(sites) { site in
                        NavigationLink(value: DetailRoute.prehistorySite(site.id)) {
                            HStack(alignment: .top, spacing: 15) {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text(site.period).font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                                    Text(site.name).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                                    Text(site.location).font(.caption).foregroundStyle(Theme.muted)
                                }
                                Spacer()
                            }.padding(.vertical, 16).contentShape(Rectangle())
                            }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("prehistoricSite_\(site.id)")
                            if site.id != sites.last?.id { Rectangle().fill(Theme.line.opacity(0.42)).frame(height: 0.5) }
                    }
                }
                if let sources = profile?.sources { SourcesView(store: store, ids: sources) }
            }.padding(.horizontal, 24).padding(.top, 22).padding(.bottom, 70)
        }
        .background(Theme.paper)
        .navigationTitle("史前遗址")
        .navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
        .navigationDestination(isPresented: $showingSite) {
            if let id = selectedSiteID { PrehistorySitePage(store: store, siteID: id) }
        }
        .accessibilityIdentifier("prehistoryPage")
    }
}

struct PrehistorySitePage: View {
    let store: HistoryStore
    let siteID: String

    var body: some View {
        if let site = store.prehistorySite(siteID) {
            ScrollView {
                VStack(alignment: .leading, spacing: 28) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(site.period).font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                        Text(site.name).font(.system(.largeTitle, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                        Text(site.location).font(.subheadline).foregroundStyle(Theme.muted)
                    }
                    Text(site.summary).font(.title3).foregroundStyle(Theme.text).lineSpacing(5)
                    SiteTextBlock(title: "发现了什么", text: site.discovery)
                    SiteTextBlock(title: "为什么重要", text: site.significance)
                    SourcesView(store: store, ids: site.sources)
                }.padding(.horizontal, 24).padding(.top, 22).padding(.bottom, 70)
            }
            .background(Theme.paper)
            .navigationTitle(site.name)
            .navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .accessibilityIdentifier("prehistorySiteDetail_\(siteID)")
        } else {
            ContentUnavailableView("未找到遗址", systemImage: "mappin.slash")
        }
    }
}

private struct SiteTextBlock: View {
    let title, text: String
    var body: some View {
        VStack(alignment: .leading, spacing: 9) {
            Text(title).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
            Text(text).font(.body).foregroundStyle(Theme.text).lineSpacing(7)
        }
    }
}
