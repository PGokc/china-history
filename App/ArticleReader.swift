import SwiftUI

private struct ReadingPositions: PreferenceKey {
    static let defaultValue: [String: CGFloat] = [:]
    static func reduce(value: inout [String: CGFloat], nextValue: () -> [String: CGFloat]) { value.merge(nextValue(), uniquingKeysWith: { _, new in new }) }
}
private struct EditorialDisclosure<Content: View>: View {
    let title: String
    let content: () -> Content
    @State private var expanded = false

    init(_ title: String, @ViewBuilder content: @escaping () -> Content) {
        self.title = title
        self.content = content
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button {
                withAnimation(.easeOut(duration: 0.2)) { expanded.toggle() }
            } label: {
                HStack(alignment: .firstTextBaseline) {
                    Text(title)
                    Spacer()
                    Text(expanded ? "收起" : "展开")
                        .font(.caption)
                        .foregroundStyle(Theme.cinnabar)
                }
                .frame(minHeight: 36)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityLabel(title)
            .accessibilityValue(expanded ? "已展开" : "已折叠")
            .accessibilityHint(expanded ? "轻点收起内容" : "轻点展开内容")

            if expanded { content() }
        }
    }
}
struct ArticleReader: View {
    let store: HistoryStore
    let personID: String
    @State private var current: String?
    @State private var resumeOffer: String?
    @State private var ready = false
    @State private var positions: [String: CGFloat] = [:]
    @StateObject private var narrator: ArticleNarrator
    init(store: HistoryStore, personID: String) {
        self.store = store; self.personID = personID
        _narrator = StateObject(wrappedValue: ArticleNarrator(dynastyID: store.dynastyID(for: personID)))
        let saved = UserDefaults.standard.string(forKey: "reading_" + personID)
        let resume = saved.flatMap { id in store.article(personID)?.sections.contains(where: { $0.id == id }) == true ? id : nil }
        _current = State(initialValue: nil)
        _resumeOffer = State(initialValue: resume)
    }
    var body: some View {
        if let article = store.article(personID) {
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 32) {
                        VStack(alignment: .leading, spacing: 14) {
                            Text(store.dynastyID(for: personID) == "xia" && store.person(personID).kind == "皇帝" ? "阅读传世夏王" : (store.person(personID).kind == "皇帝" ? "读懂这位皇帝" : "人物长读")).font(.caption).foregroundStyle(Theme.cinnabar)
                            Text(article.title).font(.system(.largeTitle, design: .serif)).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
                            Text(article.dek).font(.body).foregroundStyle(Theme.muted).lineSpacing(5)
                        }.id("opening")
                        if let resumeOffer,
                           let section = article.sections.first(where: { $0.id == resumeOffer }) {
                            VStack(alignment: .leading, spacing: 13) {
                                Text("阅读进度").font(.caption).foregroundStyle(Theme.cinnabar)
                                Text("继续上次阅读").font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                                    .accessibilityIdentifier("resumeReadingOffer")
                                Text("上次读到：\(section.title)").font(.subheadline).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
                                ViewThatFits(in: .horizontal) {
                                    HStack(spacing: 24) { resumeButtons(resumeOffer, proxy: proxy) }
                                    VStack(alignment: .leading, spacing: 8) { resumeButtons(resumeOffer, proxy: proxy) }
                                }
                            }
                            .padding(.vertical, 4)
                        }
                        ForEach(article.sections) { section in
                            VStack(alignment: .leading, spacing: 16) {
                                HStack(alignment: .firstTextBaseline, spacing: 12) {
                                    Text(section.title).font(.system(.title2, design: .serif)).foregroundStyle(Theme.ink)
                                }
                                Text(section.text).font(.body).lineSpacing(7).fixedSize(horizontal: false, vertical: true).textSelection(.enabled)
                                if !(section.people ?? []).isEmpty || !(section.events ?? []).isEmpty {
                                    EditorialDisclosure("相关人物与事件") { chapterLinks(section) }
                                        .font(.subheadline)
                                        .accessibilityIdentifier("chapterLinks_\(section.id)")
                                }
                                EditorialDisclosure("本节依据") { SourcesView(store: store, ids: section.sources, compact: true) }
                                    .font(.caption).foregroundStyle(Theme.muted)
                            }.id(section.id)
                                .background(GeometryReader { g in Color.clear.preference(key: ReadingPositions.self, value: [section.id: g.frame(in: .named("reading")).minY]) })
                        }
                        Divider()
                        if !store.associates(personID).isEmpty || store.hasFamily(personID) {
                            RelatedPeople(store: store, personID: personID, limit: 6, title: "相关人物", includeFamily: true)
                        }
                        if store.hasFamily(personID) || store.tomb(personID) != nil || !store.objects(personID).isEmpty {
                            VStack(alignment: .leading, spacing: 0) {
                                sectionTitle("继续探索")
                                if store.hasFamily(personID) {
                                    NavigationRow(title: "家族世系", subtitle: "祖先、同辈与子女", symbol: "point.3.connected.trianglepath.dotted", route: .family(personID), identifier: "articleFamily")
                                }
                                if store.tomb(personID) != nil || !store.objects(personID).isEmpty {
                                    NavigationRow(title: store.tomb(personID) == nil ? "相关遗珍" : "遗珍与陵寝", subtitle: articleHeritageSummary, symbol: "building.columns", route: .personSection(personID, .remains), identifier: "articleHeritage")
                                }
                            }
                        }
                        SourcesView(store: store, ids: article.sources)
                    }.padding(24).padding(.bottom, Theme.pageBottomAfterStandardPadding)
                }.coordinateSpace(name: "reading").background(Theme.paper).foregroundStyle(Theme.text)
                    .onPreferenceChange(ReadingPositions.self) { value in
                        positions = value
                        updateProgress(article)
                    }
                    .task {
                        guard !ready else { return }
                        do {
                            try await Task.sleep(for: .milliseconds(350))
                            ready = true
                            updateProgress(article)
                        } catch { return }
                    }
                    .onChange(of: narrator.currentSectionID) { _, sectionID in
                        guard let sectionID else { return }
                        resumeOffer = nil
                        remember(sectionID)
                        withAnimation(.easeOut(duration: 0.28)) { proxy.scrollTo(sectionID, anchor: .top) }
                    }
                    .safeAreaInset(edge: .bottom, spacing: 0) {
                        ArticleNarrationBar(article: article, visibleSectionID: current, narrator: narrator)
                    }
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Menu {
                                Button("开篇") {
                                    narrator.stop()
                                    resumeOffer = nil
                                    remember(nil)
                                    DispatchQueue.main.async {
                                        withAnimation(.easeOut(duration: 0.28)) { proxy.scrollTo("opening", anchor: .top) }
                                    }
                                }
                                ForEach(article.sections) { section in
                                    Button(section.title) {
                                        narrator.stop()
                                        resumeOffer = nil
                                        remember(section.id)
                                        DispatchQueue.main.async {
                                            withAnimation(.easeOut(duration: 0.28)) { proxy.scrollTo(section.id, anchor: .top) }
                                        }
                                    }
                                }
                            } label: { Image(systemName: "list.bullet").font(.system(size: 17, weight: .medium)).accessibilityLabel("目录") }.accessibilityIdentifier("articleContents")
                                .accessibilityValue(article.sections.first(where: { $0.id == current })?.title ?? "开篇")
                        }
                    }
                    .onDisappear { narrator.stop() }
                    .onReceive(NotificationCenter.default.publisher(for: .stopArticleNarration)) { _ in narrator.stop() }
            }.navigationTitle(store.person(personID).name).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
        } else {
            ContentUnavailableView("暂无长文", systemImage: "book.closed")
        }
    }
    private func remember(_ sectionID: String?) {
        current = sectionID
        if let sectionID { UserDefaults.standard.set(sectionID, forKey: "reading_" + personID) }
        else { UserDefaults.standard.removeObject(forKey: "reading_" + personID) }
    }
    private func updateProgress(_ article: Article) {
        guard ready, resumeOffer == nil, !positions.isEmpty, !narrator.isActive else { return }
        let sectionID = ReadingProgress.section(positions: positions, order: article.sections.map(\.id))
        if current != sectionID { remember(sectionID) }
    }
    @ViewBuilder private func resumeButtons(_ sectionID: String, proxy: ScrollViewProxy) -> some View {
        Button("继续阅读") {
            resumeOffer = nil
            remember(sectionID)
            DispatchQueue.main.async {
                withAnimation(.easeOut(duration: 0.28)) { proxy.scrollTo(sectionID, anchor: .top) }
            }
        }
        .buttonStyle(.plain)
        .font(.headline)
        .foregroundStyle(Theme.cinnabar)
        .frame(minHeight: 44)
        .accessibilityIdentifier("resumeReadingContinue")

        Button("从开篇阅读") {
            narrator.stop()
            resumeOffer = nil
            remember(nil)
            DispatchQueue.main.async {
                withAnimation(.easeOut(duration: 0.28)) { proxy.scrollTo("opening", anchor: .top) }
            }
        }
        .buttonStyle(.plain)
        .font(.headline)
        .foregroundStyle(Theme.ink)
        .frame(minHeight: 44)
        .accessibilityIdentifier("resumeReadingStartOver")
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
            }.padding(24).padding(.bottom, Theme.pageBottomAfterStandardPadding)
        }.background(Theme.paper).foregroundStyle(Theme.text).navigationTitle("\(store.person(personID).name)画像").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar).toolbarColorScheme(.light, for: .navigationBar)
    }
}
