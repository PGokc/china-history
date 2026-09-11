import SwiftUI

private struct ReadingPositions: PreferenceKey {
    static let defaultValue: [String: CGFloat] = [:]
    static func reduce(value: inout [String: CGFloat], nextValue: () -> [String: CGFloat]) { value.merge(nextValue(), uniquingKeysWith: { _, new in new }) }
}
struct ArticleReader: View {
    let store: HistoryStore
    let personID: String
    private let resume: String?
    @State private var current: String?
    @State private var ready = false
    @StateObject private var narrator = ArticleNarrator()
    init(store: HistoryStore, personID: String) {
        self.store = store; self.personID = personID
        resume = UserDefaults.standard.string(forKey: "reading_" + personID)
    }
    var body: some View {
        if let article = store.article(personID) {
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 32) {
                        VStack(alignment: .leading, spacing: 14) {
                            Text(store.person(personID).kind == "皇帝" ? "读懂这位皇帝" : "人物长读").font(.caption).foregroundStyle(Theme.cinnabar)
                            Text(article.title).font(.system(.largeTitle, design: .serif)).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
                            Text(article.dek).font(.body).foregroundStyle(Theme.muted).lineSpacing(5)
                        }.id("opening")
                        ForEach(article.sections) { section in
                            VStack(alignment: .leading, spacing: 16) {
                                HStack(alignment: .firstTextBaseline, spacing: 12) {
                                    Text(section.title).font(.system(.title2, design: .serif)).foregroundStyle(Theme.ink)
                                }
                                Text(section.text).font(.body).lineSpacing(7).fixedSize(horizontal: false, vertical: true).textSelection(.enabled)
                                if !(section.people ?? []).isEmpty || !(section.events ?? []).isEmpty {
                                    DisclosureGroup("相关人物与事件") { chapterLinks(section).padding(.top, 8) }
                                        .font(.subheadline).tint(Theme.muted)
                                        .accessibilityIdentifier("chapterLinks_\(section.id)")
                                }
                                DisclosureGroup("本节依据") { SourcesView(store: store, ids: section.sources, compact: true).padding(.top, 10) }
                                    .font(.caption).foregroundStyle(Theme.muted)
                            }.id(section.id)
                                .background(GeometryReader { g in Color.clear.preference(key: ReadingPositions.self, value: [section.id: g.frame(in: .named("reading")).minY]) })
                        }
                        Divider()
                        if !store.associates(personID).isEmpty || store.hasFamily(personID) {
                            RelatedPeople(store: store, personID: personID, limit: 6, title: "相关人物", includeFamily: true)
                        }
                        VStack(alignment: .leading, spacing: 0) {
                            sectionTitle("继续探索")
                            if store.hasFamily(personID) {
                                NavigationRow(title: "家族世系", subtitle: "祖先、同辈与子女", symbol: "point.3.connected.trianglepath.dotted", route: .family(personID), identifier: "articleFamily")
                            }
                            if store.tomb(personID) != nil || !store.objects(personID).isEmpty {
                                NavigationRow(title: store.tomb(personID) == nil ? "相关遗珍" : "遗珍与陵寝", subtitle: articleHeritageSummary, symbol: "building.columns", route: .personSection(personID, .remains), identifier: "articleHeritage")
                            }
                        }
                        SourcesView(store: store, ids: article.sources)
                    }.padding(24).padding(.bottom, 28)
                }.coordinateSpace(name: "reading").background(Theme.paper).foregroundStyle(Theme.text)
                    .onPreferenceChange(ReadingPositions.self) { positions in
                        guard ready, let closest = positions.min(by: { abs($0.value - 80) < abs($1.value - 80) })?.key else { return }
                        current = closest; UserDefaults.standard.set(closest, forKey: "reading_" + personID)
                    }
                    .task {
                        guard !ready else { return }
                        if let resume, article.sections.contains(where: { $0.id == resume }) {
                            try? await Task.sleep(for: .milliseconds(150))
                            proxy.scrollTo(resume, anchor: .top)
                        }
                        try? await Task.sleep(for: .milliseconds(350)); ready = true
                    }
                    .onChange(of: narrator.currentSectionID) { _, sectionID in
                        guard let sectionID else { return }
                        current = sectionID
                        UserDefaults.standard.set(sectionID, forKey: "reading_" + personID)
                        withAnimation(.easeOut(duration: 0.28)) { proxy.scrollTo(sectionID, anchor: .top) }
                    }
                    .safeAreaInset(edge: .bottom, spacing: 0) {
                        ArticleNarrationBar(article: article, visibleSectionID: current ?? resume, narrator: narrator)
                    }
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Menu {
                                Button("开篇") { proxy.scrollTo("opening", anchor: .top); UserDefaults.standard.removeObject(forKey: "reading_" + personID) }
                                ForEach(article.sections) { section in Button(section.title) { proxy.scrollTo(section.id, anchor: .top); current = section.id; UserDefaults.standard.set(section.id, forKey: "reading_" + personID) } }
                            } label: { Image(systemName: "list.bullet").font(.system(size: 17, weight: .medium)).accessibilityLabel("目录") }.accessibilityIdentifier("articleContents")
                        }
                    }
                    .onDisappear { narrator.stop() }
                    .onReceive(NotificationCenter.default.publisher(for: .stopArticleNarration)) { _ in narrator.stop() }
            }.navigationTitle(store.person(personID).name).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
        } else {
            ContentUnavailableView("暂无长文", systemImage: "book.closed")
        }
    }
    private var articleHeritageSummary: String {
        let names = [store.tomb(personID)?.title].compactMap { $0 } + store.objects(personID).map(\.title)
        return names.prefix(2).joined(separator: "、")
    }
    @ViewBuilder func chapterLinks(_ section: ArticleSection) -> some View {
        let people = section.people ?? []
        let events = section.events ?? []
        if !people.isEmpty || !events.isEmpty {
            VStack(alignment: .leading, spacing: 2) {
                ForEach(people, id: \.self) { id in
                    NavigationLink(value: DetailRoute.person(id)) {
                        HStack { VStack(alignment: .leading, spacing: 3) { Text(store.person(id).name); Text(store.person(id).call).font(.caption).foregroundStyle(Theme.muted) }; Spacer() }
                            .font(.subheadline).frame(minHeight: 44).contentShape(Rectangle())
                    }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("chapterPerson_\(section.id)_\(id)")
                }
                ForEach(events, id: \.self) { id in
                    if let event = store.content.events.first(where: { $0.id == id }) {
                        NavigationLink(value: DetailRoute.event(id)) {
                            HStack { VStack(alignment: .leading, spacing: 3) { Text(event.year).font(.caption).foregroundStyle(Theme.cinnabar); Text(event.title) }; Spacer() }
                                .font(.subheadline).frame(minHeight: 44).contentShape(Rectangle())
                        }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("chapterEvent_\(section.id)_\(id)")
                    }
                }
            }.foregroundStyle(Theme.ink)
        }
    }
}
struct PortraitPage: View {
    let store: HistoryStore
    let personID: String
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                if let label = store.portrait(personID)?.displayLabel { Text(label).font(.subheadline).foregroundStyle(Theme.cinnabar) }
                if let name = store.image(personID) {
                    LocalImage(name: name).frame(maxWidth: .infinity).frame(height: 480)
                } else { LocalImage(name: nil).frame(height: 230).frame(maxWidth: .infinity) }
                if let p = store.portrait(personID) {
                    Text(p.title).font(.system(.title2, design: .serif)).foregroundStyle(Theme.ink)
                    ForEach([("作者/归属",p.attribution),("作品年代",p.date),("收藏/图像提供",p.collection)], id: \.0) { key, value in
                        VStack(alignment: .leading, spacing: 5) { Text(key).font(.caption).foregroundStyle(Theme.muted); Text(value).font(.body) }
                    }
                    Text(p.description).lineSpacing(6)
                    
                    SourcesView(store: store, ids: p.sourceIds)
                } else {
                    Text(store.person(personID).name).font(.system(.title2, design: .serif))
                    Text("人物画像").font(.caption).foregroundStyle(Theme.muted)
                    Text("暂无可确认的人物画像。").foregroundStyle(Theme.muted)
                }
                Text("历史画像未必是生前写生；作品资料及图像说明见原始出处。").font(.caption).foregroundStyle(Theme.muted)
            }.padding(24)
        }.background(Theme.paper).foregroundStyle(Theme.text).navigationTitle("\(store.person(personID).name)画像").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
    }
}
