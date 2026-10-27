import XCTest

final class MingJiUITests: XCTestCase {
    @MainActor func launch(_ large: Bool = false, enterFamily: Bool = true) -> XCUIApplication {
        let app = XCUIApplication(); app.launchArguments = ["--uitesting"]
        if large { app.launchArguments += ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"] }
        app.launch(); XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        if enterFamily { app.tabBars.buttons["家族"].tap(); XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 10)) }
        return app
    }
    @MainActor func shot(_ name: String, _ app: XCUIApplication) {
        Thread.sleep(forTimeInterval: 1)
        let attachment = XCTAttachment(screenshot: app.screenshot()); attachment.name = name; attachment.lifetime = .keepAlways; add(attachment)
        let tree = XCTAttachment(string: app.debugDescription); tree.name = name + "-tree"; tree.lifetime = .keepAlways; add(tree)
    }
    @MainActor func reach(_ element: XCUIElement, in app: XCUIApplication, attempts: Int = 8) {
        for _ in 0..<attempts { if element.isHittable { return }; app.swipeUp() }
        XCTAssertTrue(element.isHittable)
    }
    @MainActor func assertCompactPageEnding(_ element: XCUIElement, in app: XCUIApplication, attempts: Int = 18, file: StaticString = #filePath, line: UInt = #line) {
        reach(element, in: app, attempts: attempts)
        for _ in 0..<3 { app.swipeUp() }
        let gap = app.tabBars.firstMatch.frame.minY - element.frame.maxY
        XCTAssertGreaterThan(gap, 16, file: file, line: line)
        XCTAssertLessThan(gap, 68, file: file, line: line)
    }
    @MainActor func openArticle(in app: XCUIApplication) {
        if !app.buttons["articleEntry"].exists {
            reach(app.buttons["personHero"], in: app); app.buttons["personHero"].tap()
            XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        }
        reach(app.buttons["articleEntry"], in: app); app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5))
    }
    @MainActor func testV28TimeMapFiltersAndKeepsNavigation() throws {
        let app = launch(enterFamily: false)
        app.buttons["dynasty_prehistory"].tap()
        let slider = app.sliders["historyTimeSlider"]
        XCTAssertTrue(slider.waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["约公元前3000年"].exists)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_liangzhu"].exists)
        XCTAssertFalse(app.buttons["contemporary_hemudu"].exists)
        app.buttons["完成"].tap()
        slider.adjust(toNormalizedSliderPosition: 0)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_hemudu"].exists)
        XCTAssertFalse(app.buttons["contemporary_liangzhu"].exists)
        app.buttons["contemporary_hemudu"].tap()
        XCTAssertTrue(app.navigationBars["河姆渡遗址"].waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.buttons["完成"].tap()
        slider.adjust(toNormalizedSliderPosition: 1)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_shimao"].exists)
        XCTAssertFalse(app.buttons["contemporary_hemudu"].exists)
        app.buttons["完成"].tap()
        for _ in 0..<3 { app.swipeDown() }
        let earlyScale = app.segmentedControls.firstMatch.buttons["远古人类"]
        XCTAssertTrue(earlyScale.isHittable)
        earlyScale.tap()
        let earlyDate = app.staticTexts["timelineDate"]
        expectation(for: NSPredicate(format: "label == %@", "距今约170万年"), evaluatedWith: earlyDate)
        waitForExpectations(timeout: 5)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_yuanmou"].waitForExistence(timeout: 5))
        app.buttons["完成"].tap()
        app.segmentedControls.firstMatch.buttons["文明起源"].tap()
        shot("v28-time-map", app)
    }
    @MainActor func testV109PrehistoryOpensOnMapAndUsesOneGroupedGuide() throws {
        let app = launch(enterFamily: false)
        XCTAssertTrue(app.buttons["dynasty_prehistory"].waitForExistence(timeout: 5))
        app.buttons["dynasty_prehistory"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryPage"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryTimeMap"].exists)
        XCTAssertTrue(app.sliders["historyTimeSlider"].exists)
        XCTAssertFalse(app.buttons["prehistoryTimelineEntry"].exists)
        XCTAssertTrue(app.staticTexts["在时间中观察遗址"].exists)
        shot("v109-prehistory-map-first", app)

        let guide = app.staticTexts["prehistorySiteGuide"]
        reach(guide, in: app, attempts: 14)
        XCTAssertTrue(guide.exists)
        XCTAssertTrue(app.staticTexts["远古人类"].exists)
        reach(app.staticTexts["复杂聚落"], in: app, attempts: 20)
        XCTAssertTrue(app.staticTexts["定居与农业"].exists)
        XCTAssertTrue(app.staticTexts["复杂聚落"].exists)
        XCTAssertTrue(app.buttons["prehistoricGuide_shimao"].exists)
        shot("v109-prehistory-grouped-guide", app)
    }

    @MainActor func testV110FiveUserExperienceRounds() throws {
        let navigation = launch(enterFamily: false)
        navigation.buttons["dynasty_prehistory"].tap()
        XCTAssertTrue(navigation.descendants(matching: .any)["prehistoryPage"].waitForExistence(timeout: 5))
        navigation.navigationBars.buttons.element(boundBy: 0).tap()
        XCTAssertEqual(navigation.buttons["dynasty_ming"].value as? String, "已选中")
        XCTAssertNotEqual(navigation.buttons["dynasty_prehistory"].value as? String, "已选中")
        navigation.terminate()

        let overview = XCUIApplication()
        overview.launchArguments = ["--uitesting", "--ui-dynasty", "qing"]
        overview.launch()
        XCTAssertTrue(overview.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        reach(overview.buttons["dynasty_qing"], in: overview, attempts: 14); overview.buttons["dynasty_qing"].tap()
        XCTAssertTrue(overview.staticTexts["dynastyDestinationsTitle"].waitForExistence(timeout: 5))
        XCTAssertTrue(overview.buttons["dynastySequence_qing"].exists)
        XCTAssertLessThan(overview.staticTexts["dynastyDestinationsTitle"].frame.minY, overview.staticTexts["朝代总览"].frame.minY)
        shot("v110-dynasty-destinations-first", overview)
        overview.terminate()

        let large = launch(true)
        large.buttons["personHero"].tap()
        XCTAssertTrue(large.staticTexts["personSummary"].waitForExistence(timeout: 5))
        XCTAssertFalse(large.buttons["人物简介"].exists)
        shot("v110-large-text-summary", large)
        large.terminate()

        let collection = XCUIApplication()
        collection.launchArguments = ["--uitesting", "--ui-dynasty", "qing"]
        collection.launch()
        XCTAssertTrue(collection.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        collection.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(collection.staticTexts["collectionCount_ideas"].waitForExistence(timeout: 5))
        XCTAssertTrue(collection.staticTexts["collectionCount_objects"].exists)
        XCTAssertTrue(collection.staticTexts["collectionCount_tombs"].exists)
        shot("v110-collection-counts", collection)
        collection.terminate()

        let continuity = launch()
        chooseChild("biao", in: continuity)
        XCTAssertTrue(continuity.buttons["personHero"].label.contains("朱标"))
        continuity.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(continuity.buttons["succession_0"].waitForExistence(timeout: 5))
        continuity.tabBars.buttons["家族"].tap()
        XCTAssertTrue(continuity.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(continuity.buttons["personHero"].label.contains("朱标"))
        shot("v110-family-continuity", continuity)
    }

    @MainActor func testV27DynastyMetadataAndMapLinks() throws {
        let app = launch(enterFamily: false)
        XCTAssertFalse(app.staticTexts["正在探索 · 明"].exists)
        app.buttons["dynasty_prehistory"].tap()
        shot("v27-map-overview", app)
        XCTAssertTrue(app.sliders["historyTimeSlider"].exists)
        let hemudu = app.buttons["prehistoricGuide_hemudu"]
        reach(hemudu, in: app, attempts: 14)
        shot("v27-map", app)
        hemudu.tap()
        XCTAssertTrue(app.navigationBars["河姆渡遗址"].waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        XCTAssertEqual(app.buttons["dynasty_ming"].value as? String, "已选中")
        XCTAssertNotEqual(app.buttons["dynasty_prehistory"].value as? String, "已选中")
        shot("v27-dynasty", app)
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.staticTexts["庙号 太祖"].exists)
        XCTAssertTrue(app.staticTexts["年号 洪武"].exists)
        XCTAssertTrue(app.staticTexts["在位 1368—1398"].exists)
        shot("v27-sequence", app)
    }

    @MainActor func testV30SuccessionUsesCompactHierarchy() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.buttons["succession_0"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["年号 洪武"].exists)
        XCTAssertTrue(app.staticTexts["在位 1368—1398"].exists)
        XCTAssertFalse(app.staticTexts["父 → 子"].exists)

        reach(app.buttons["succession_6"], in: app, attempts: 10)
        XCTAssertTrue(app.staticTexts["年号 景泰"].exists)
        XCTAssertTrue(app.staticTexts["土木之变后入继"].exists)
        XCTAssertFalse(app.staticTexts["后世绣像"].exists)
        shot("v30-sequence-hierarchy", app)
    }

    @MainActor func testV31TombsUseGroupedTwoColumnHierarchy() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap()
        app.buttons["collectionCategory_tombs"].tap()
        XCTAssertTrue(app.navigationBars["帝王陵寝"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["南京"].exists)
        XCTAssertTrue(app.staticTexts["明孝陵"].exists)
        XCTAssertFalse(app.staticTexts["明孝陵（南京）"].exists)
        reach(app.buttons["tomb_di"], in: app, attempts: 5)
        XCTAssertTrue(app.staticTexts["明十三陵"].exists)
        XCTAssertTrue(app.staticTexts["长陵"].exists)
        XCTAssertTrue(app.staticTexts["朱棣"].exists)
        XCTAssertTrue(app.staticTexts["永乐"].exists)
        shot("v31-tomb-hierarchy", app)
    }
    @MainActor func testV25ReadingControls() throws {
        let app = launch(); openArticle(in: app)
        XCTAssertTrue(app.buttons["开始朗读"].isHittable)
        XCTAssertGreaterThanOrEqual(app.buttons["开始朗读"].frame.width, 44)
        app.buttons["朗读设置"].tap()
        XCTAssertTrue(app.navigationBars["朗读设置"].waitForExistence(timeout: 5))
        XCTAssertFalse(app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] %@", "豆包")).firstMatch.exists)
        XCTAssertFalse(app.staticTexts["备用声音"].exists)
        app.buttons["完成"].tap()
        XCTAssertTrue(app.buttons["articleContents"].isHittable)
        shot("v25-reader", app)
    }
    @MainActor func testFamilyExplorationAndFreshEntry() throws {
        let app = launch(); shot("01-family", app)
        app.buttons["relative_ma"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("马氏"))
        XCTAssertTrue(app.buttons["relative_biao"].exists); shot("02-mother-children",app)
        app.buttons["relative_biao"].tap()
        XCTAssertTrue(app.buttons["relative_ma"].exists)
        app.buttons["relative_yuanzhang"].tap()
        chooseChild("di", in:app)
        app.buttons["relative_gaochi"].tap()
        app.buttons["personHero"].swipeLeft()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱高煦"))
        app.buttons["personHero"].swipeRight()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱高炽"))
        app.buttons["relative_zhanji"].tap()
        app.terminate(); app.launchArguments = []; app.launch(); XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10)); app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 10))
        let founderShown = NSPredicate(format: "label CONTAINS %@", "朱元璋")
        expectation(for: founderShown, evaluatedWith: app.buttons["personHero"])
        waitForExpectations(timeout: 3)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout: 5))
        app.buttons["portraitEntry"].tap(); shot("03-portrait",app)
    }
    @MainActor func testArticleAndChapterRestoration() throws {
        let app = launch(); openArticle(in: app)
        Thread.sleep(forTimeInterval:1)
        app.buttons["articleContents"].tap();app.buttons["开篇"].tap();shot("04-article",app)
        app.buttons["articleContents"].tap()
        app.buttons["1368年为什么值得单独记住"].tap();shot("05-chapter",app)
        XCTAssertEqual(app.buttons["articleContents"].value as? String, "1368年为什么值得单独记住")
        app.terminate();app.launch(); XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10)); app.tabBars.buttons["家族"].tap()
        openArticle(in: app)
        XCTAssertTrue(app.descendants(matching: .any)["resumeReadingOffer"].waitForExistence(timeout: 5))
        app.buttons["resumeReadingContinue"].tap()
        XCTAssertTrue(app.staticTexts["1368年为什么值得单独记住"].isHittable)
    }

    @MainActor func testV111ReadingChoiceLargeTitleAndSearchSuggestions() throws {
        let reader = launch(); openArticle(in: reader)
        reader.buttons["articleContents"].tap(); reader.buttons["1368年为什么值得单独记住"].tap()
        reader.navigationBars.buttons.element(boundBy: 0).tap(); openArticle(in: reader)
        XCTAssertTrue(reader.descendants(matching: .any)["resumeReadingOffer"].waitForExistence(timeout: 5))
        XCTAssertTrue(reader.buttons["resumeReadingContinue"].exists)
        XCTAssertTrue(reader.buttons["resumeReadingStartOver"].exists)
        shot("v111-reading-choice", reader)
        reader.buttons["resumeReadingStartOver"].tap()
        XCTAssertEqual(reader.buttons["articleContents"].value as? String, "开篇")
        reader.terminate()

        let large = launch(true)
        large.buttons["personHero"].tap()
        let name = large.staticTexts["personName"]
        XCTAssertTrue(name.waitForExistence(timeout: 5))
        XCTAssertLessThan(name.frame.height, 65)
        XCTAssertTrue(large.staticTexts["personSummary"].exists)
        shot("v111-large-person-title", large)
        large.terminate()

        let search = launch(enterFamily: false)
        search.buttons["globalSearch"].tap()
        XCTAssertTrue(search.buttons["searchSuggestion_北京人"].waitForExistence(timeout: 5))
        search.buttons["searchSuggestion_北京人"].tap()
        XCTAssertTrue(search.staticTexts["searchResultCount"].waitForExistence(timeout: 5))
        XCTAssertTrue(search.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "search_site_")).firstMatch.exists)
        shot("v111-search-suggestion", search)
    }
    @MainActor func testV12ArticleNarrationControls() throws {
        let app = launch(); openArticle(in: app)
        XCTAssertTrue(app.buttons["narrationToggle"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["narrationSettings"].exists)
        XCTAssertTrue(app.buttons["narrationPrevious"].exists)
        XCTAssertTrue(app.buttons["narrationNext"].exists)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        app.buttons["narrationSettings"].tap()
        XCTAssertTrue(app.navigationBars["朗读设置"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["narrationSpeed_标准"].exists)
        XCTAssertEqual(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "narrationVoice_")).count, 0)
        app.buttons["完成"].tap()
        app.buttons["narrationToggle"].tap()
        XCTAssertEqual(app.buttons["narrationToggle"].label, "暂停朗读")
        XCTAssertTrue(app.sliders["narrationProgress"].waitForExistence(timeout: 5))
        app.tabBars.buttons["朝代"].tap()
        app.tabBars.buttons["家族"].tap()
        openArticle(in: app)
        XCTAssertTrue(app.buttons["narrationToggle"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v12-article-narration", app)
    }

    @MainActor func testV85OnDemandNarrationDownloadsAndPlays() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 10))
        openArticle(in: app)
        let toggle = app.buttons["narrationToggle"]
        toggle.tap()
        expectation(for: NSPredicate(format: "label == %@", "暂停朗读"), evaluatedWith: toggle)
        waitForExpectations(timeout: 30)
        let progress = app.sliders["narrationProgress"]
        XCTAssertTrue(progress.waitForExistence(timeout: 5))
        progress.adjust(toNormalizedSliderPosition: 0.45)
        toggle.tap()
        XCTAssertEqual(toggle.label, "继续朗读")
        shot("v85-on-demand-narration", app)
    }
    @MainActor func testArtifactAndTombReturnContext() throws {
        let app = launch();app.tabBars.buttons["遗珍"].tap();shot("06-objects",app)
        app.buttons["collectionCategory_objects"].tap()
        app.buttons["artifact_porcelain"].tap()
        XCTAssertTrue(app.staticTexts["观看提示"].waitForExistence(timeout:5));shot("07-object-detail",app)
        reach(app.buttons["explore_zhanji"],in:app);app.buttons["explore_zhanji"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:5));XCTAssertTrue(app.buttons["personHero"].label.contains("朱瞻基"))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_zhanji"].waitForExistence(timeout:5));XCTAssertTrue(app.buttons["explore_zhanji"].isHittable)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.buttons["collectionCategory_tombs"].tap();shot("08-tombs",app)
        app.buttons["tomb_yuanzhang"].tap();XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout:5));shot("09-tomb-detail",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["tomb_yunwen"],in:app);app.buttons["tomb_yunwen"].tap()
        XCTAssertTrue(app.staticTexts["尚无定论"].waitForExistence(timeout:5))
    }
    @MainActor func testLargeTypeReading() throws {
        let app = launch(true);shot("10-large-family",app)
        reach(app.buttons["personHero"],in:app);app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout:5));shot("11-large-person",app)
        reach(app.buttons["articleEntry"],in:app);app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("12-large-article",app)
    }

    @MainActor func testVerticalDragPreservesFocusedPerson() throws {
        let app = launch()
        chooseChild("di", in:app);app.buttons["relative_gaochi"].tap()
        let hero = app.buttons["personHero"]
        hero.coordinate(withNormalizedOffset: CGVector(dx:0.5,dy:0.8)).press(forDuration:0.05, thenDragTo:hero.coordinate(withNormalizedOffset:CGVector(dx:0.5,dy:0.1)))
        XCTAssertTrue(hero.label.contains("朱高炽"))
        XCTAssertFalse(app.buttons["portraitEntry"].exists)
        app.swipeDown()
        XCTAssertTrue(hero.isHittable)
    }

    @MainActor func testFiguresHaveArticlesAndReturnLinks() throws {
        let app = launch();reach(app.buttons["allAssociates"],in:app);app.buttons["allAssociates"].tap()
        reach(app.buttons["associate_lishanzhang"],in:app);app.buttons["associate_lishanzhang"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("13-figure",app)
        reach(app.buttons["articleEntry"],in:app);app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("14-figure-article",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        openAssociates(in:app);reach(app.buttons["associate_yuanzhang"],in:app);app.buttons["associate_yuanzhang"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout:5))
        XCTAssertTrue(app.staticTexts["洪武皇帝"].exists)
    }

    @MainActor func openEmperor(_ sequence: String, in app: XCUIApplication) {
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_" + sequence], in: app)
        app.buttons["succession_" + sequence].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
    }
    @MainActor func testV3ChapterEventPersonReturn() throws {
        let app = launch(); openEmperor("5", in: app)
        shot("v3-01-yingzong-family",app)
        openArticle(in: app)
        Thread.sleep(forTimeInterval:1)
        app.buttons["articleContents"].tap();app.buttons["1449年，御驾成了俘虏"].tap()
        let links = app.buttons["chapterLinks_qizhen-3"]
        reach(links,in:app); links.tap()
        let event = app.buttons["chapterEvent_qizhen-3_v2e_tumu"]
        reach(event,in:app);shot("v3-02-chapter-links",app);event.tap()
        XCTAssertTrue(app.staticTexts["发生了什么"].waitForExistence(timeout:5))
        reach(app.buttons["explore_esen"],in:app);shot("v3-03-event-network",app);app.buttons["explore_esen"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("v3-04-esen",app)
        XCTAssertFalse(app.buttons["explore_esen"].exists)
        app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("v3-05-esen-article",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_esen"].isHittable)
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(event.isHittable)
    }
    @MainActor func testV3JingtaiConnectionsAndTomb() throws {
        let app = launch();openEmperor("6",in:app)
        app.buttons["personHero"].tap()
        reach(app.buttons["category_remains"],in:app);app.buttons["category_remains"].tap();app.buttons["tombCard"].tap()
        XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout:5));shot("v3-06-jingtai-tomb",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap();openAssociates(in:app);reach(app.buttons["associate_yuqian"],in:app);app.buttons["associate_yuqian"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("v3-07-yuqian",app)
        XCTAssertFalse(app.buttons["explore_yuqian"].exists)
        openAssociates(in:app);reach(app.buttons["associate_jianshen"],in:app);app.buttons["associate_jianshen"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["associate_jianshen"].isHittable)
    }
    @MainActor func testV3TempleToPeopleLoop() throws {
        let app = launch();app.tabBars.buttons["遗珍"].tap()
        reach(app.buttons["artifact_zhihua"],in:app);app.buttons["artifact_zhihua"].tap()
        XCTAssertTrue(app.staticTexts["观看提示"].waitForExistence(timeout:5));shot("v3-08-zhihua",app)
        reach(app.buttons["explore_wangzhen"],in:app);app.buttons["explore_wangzhen"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("v3-09-wangzhen",app)
        XCTAssertFalse(app.buttons["explore_wangzhen"].exists)
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_wangzhen"].isHittable)
        app.buttons["explore_qizhen"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱祁镇"))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_qizhen"].isHittable)
    }
    @MainActor func chooseChild(_ id: String, in app: XCUIApplication) {
        if app.buttons["relative_" + id].exists {
            reach(app.buttons["relative_" + id],in:app);app.buttons["relative_" + id].tap()
        } else {
            reach(app.buttons["allChildren"],in:app);app.buttons["allChildren"].tap()
            reach(app.buttons["member_" + id],in:app);app.buttons["member_" + id].tap()
        }
    }
    @MainActor func openAssociates(in app: XCUIApplication) {
        reach(app.buttons["category_relationships"],in:app);app.buttons["category_relationships"].tap()
        reach(app.buttons["allAssociates"],in:app);app.buttons["allAssociates"].tap()
    }
    @MainActor func testV4OverviewAndPrinces() throws {
        let app = launch();shot("v4-01-family",app)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5))
        XCTAssertTrue(app.segmentedControls.firstMatch.exists)
        XCTAssertTrue(app.buttons["category_events"].exists)
        XCTAssertTrue(app.buttons["event_founding"].exists)
        shot("v4-02-person-overview",app)
        reach(app.buttons["category_relationships"],in:app)
        app.buttons["category_relationships"].tap();shot("v4-03-relationships",app)
        app.buttons["allChildren"].tap();shot("v4-04-princes",app)
        for id in ["biao","shang","gang","di","su","bai","quan"] { XCTAssertTrue(app.buttons["member_" + id].exists) }
        app.buttons["member_shang"].tap();app.buttons["personHero"].tap()
        XCTAssertFalse(app.buttons["category_remains"].exists)
        XCTAssertFalse(app.buttons["portraitEntry"].exists)
        app.navigationBars.buttons.element(boundBy:0).tap();app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["member_bai"],in:app);app.buttons["member_bai"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱柏"));shot("v4-05-xiang-family",app)
        app.buttons["personHero"].tap();shot("v4-06-xiang-overview",app)
        XCTAssertTrue(app.buttons["category_remains"].exists)
        app.buttons["category_relationships"].tap()
        XCTAssertTrue(app.buttons["parent_yuanzhang"].isHittable)
        app.buttons["parent_yuanzhang"].tap()
        XCTAssertTrue(app.staticTexts["朱元璋"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("v4-07-xiang-article",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["category_events"],in:app);app.buttons["category_events"].tap();shot("v4-08-xiang-events",app)
        XCTAssertGreaterThan(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "event_")).count, 0)
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["category_remains"],in:app);app.buttons["category_remains"].tap()
        app.buttons["personObject_v4p_xiangcenotaph"].tap();shot("v4-16-xiang-cenotaph",app)
        XCTAssertTrue(app.staticTexts["观看提示"].exists)
    }
    @MainActor func testV4CategoriesAndSources() throws {
        let app = launch();app.buttons["personHero"].tap()
        reach(app.buttons["category_events"],in:app);app.buttons["category_events"].tap()
        reach(app.buttons["event_founding"],in:app);app.buttons["event_founding"].tap()
        XCTAssertTrue(app.staticTexts["发生了什么"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["event_founding"].isHittable)
        app.terminate(); app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout:10))
        app.tabBars.buttons["家族"].tap(); XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:10)); app.buttons["personHero"].tap()
        reach(app.buttons["category_remains"],in:app);app.buttons["category_remains"].tap();shot("v4-09-remains",app)
        app.buttons["tombCard"].tap();XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["category_records"],in:app);app.buttons["category_records"].tap();shot("v4-10-records",app)
        XCTAssertTrue(app.staticTexts["年号纪年"].exists)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.swipeDown();reach(app.buttons["portraitEntry"],in:app);app.buttons["portraitEntry"].tap();shot("v4-11-portrait",app)
    }
    @MainActor func testV4LargeTypeHierarchy() throws {
        let app = launch(true);app.buttons["personHero"].tap();shot("v4-12-large-overview",app)
        reach(app.buttons["category_relationships"],in:app);shot("v4-13-large-categories",app);app.buttons["category_relationships"].tap()
        reach(app.buttons["allChildren"],in:app);app.buttons["allChildren"].tap()
        reach(app.buttons["member_bai"],in:app);shot("v4-14-large-princes",app);app.buttons["member_bai"].tap()
        app.buttons["personHero"].tap()
        reach(app.buttons["category_relationships"],in:app);app.buttons["category_relationships"].tap()
        XCTAssertTrue(app.buttons["parent_yuanzhang"].isHittable);shot("v4-15-large-parent",app)
    }

    @MainActor func testV4HistoricalPortraitLabels() throws {
        for (sequence,id,label) in [("1","yunwen","传说形象"),("6","qiyu","后世绣像"),("16","youjian","后世绣像")] {
            let app = launch();openEmperor(sequence,in:app)
            XCTAssertTrue(app.buttons["personHero"].label.contains(label))
            app.buttons["personHero"].tap()
            XCTAssertTrue(app.staticTexts[label].waitForExistence(timeout:5));shot("v4-portrait-" + id + "-overview",app)
            app.buttons["portraitEntry"].tap()
            XCTAssertTrue(app.staticTexts[label].waitForExistence(timeout:5));shot("v4-portrait-" + id + "-source",app)
            app.terminate()
        }
    }

    @MainActor func testV5DynastySelectionAndPersistence() throws {
        let app = launch(enterFamily: false)
        XCTAssertEqual(app.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        XCTAssertTrue(app.descendants(matching: .any)["dynasty_qin"].exists)
        XCTAssertTrue(app.buttons["dynasty_qin"].exists)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap(); shot("v5-01-dynasties-qing", app)
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("努尔哈赤")); shot("v5-02-qing-family", app)
        chooseChild("q_hongtaiji", in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("皇太极"))
        app.terminate(); app.launchArguments = []; app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14)
        XCTAssertEqual(app.buttons["dynasty_qing"].value as? String, "已选中")
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("皇太极")); shot("v5-03-qing-restored", app)
    }

    @MainActor func testV8EveryDynastyOpensAnIntroduction() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qin"], in: app, attempts: 12)
        app.buttons["dynasty_qin"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyDetail_qin"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["短暂统一与长久制度遗产"].exists)
        XCTAssertTrue(app.staticTexts["朝代总览"].exists)
        XCTAssertTrue(app.descendants(matching: .any)["territoryMap_qin"].exists)
        shot("v8-01-qin-introduction", app)
    }

    @MainActor func testV8PrehistoryMapAndSiteReading() throws {
        let app = launch(enterFamily: false)
        XCTAssertTrue(app.buttons["dynasty_prehistory"].waitForExistence(timeout: 5))
        app.buttons["dynasty_prehistory"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryPage"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryTimeMap"].exists)
        reach(app.buttons["prehistoricGuide_hemudu"], in: app, attempts: 16)
        app.buttons["prehistoricGuide_hemudu"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistorySiteDetail_hemudu"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["水湿环境保存了什么"].exists)
        XCTAssertTrue(app.staticTexts["稻作与多样食物"].exists)
        shot("v8-02-hemudu-detail", app)
    }

    @MainActor func testV5QingSequenceArticleAndTombs() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.staticTexts["从后金兴起到帝制终结，皇位传承始终与宗室、摄政和时代转折相连。努尔哈赤与皇太极属于入关前的两代统治者。"].waitForExistence(timeout: 5))
        reach(app.buttons["succession_q_5"], in: app, attempts: 14); app.buttons["succession_q_5"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("弘历")); app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5)); app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5)); shot("v5-04-qianlong-article", app)
        app.tabBars.buttons["遗珍"].tap(); app.buttons["collectionCategory_tombs"].tap()
        reach(app.buttons["tomb_q_daoguang"], in: app, attempts: 16); app.buttons["tomb_q_daoguang"].tap()
        XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout: 5)); XCTAssertTrue(app.staticTexts["慕陵"].exists); shot("v5-05-muling", app)
        app.navigationBars.buttons.element(boundBy: 0).tap()
        reach(app.buttons["tomb_q_xuantong"], in: app, attempts: 16); app.buttons["tomb_q_xuantong"].tap()
        XCTAssertTrue(app.staticTexts["特殊安葬"].waitForExistence(timeout: 5)); shot("v5-06-puyi-burial", app)
    }

    @MainActor func testV5LargeTypeDynastyAndQingOverview() throws {
        let app = launch(true, enterFamily: false); shot("v5-07-large-dynasties", app)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 18); app.buttons["dynasty_qing"].tap(); app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5)); app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["category_relationships"].waitForExistence(timeout: 5)); shot("v5-08-large-qing-overview", app)
    }

    @MainActor func testV5PuyiBiologicalAndRitualLineage() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_q_11"], in: app, attempts: 18); app.buttons["succession_q_11"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("溥仪"))
        XCTAssertTrue(app.buttons["relative_q_zaifeng"].label.contains("父亲"))
        XCTAssertTrue(app.buttons["relative_q_tongzhi"].label.contains("礼制承继"))
        XCTAssertTrue(app.buttons["relative_q_guangxu"].label.contains("礼制承继"))
        shot("v5-09-puyi-lineage", app)
        app.buttons["relative_q_zaifeng"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("载沣"))
        openArticle(in: app)
    }

    @MainActor func testV6TabOrderAndCategorizedMajorEvents() throws {
        let app = launch(enterFamily: false)
        XCTAssertEqual(app.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_0"], in: app); app.buttons["succession_0"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5)); app.buttons["personHero"].tap()
        reach(app.buttons["eventCategory_政治"], in: app)
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            let tab = app.buttons["eventCategory_\(category)"]
            XCTAssertTrue(tab.exists)
            XCTAssertTrue(tab.isHittable)
        }
        app.buttons["eventCategory_军事"].tap()
        reach(app.buttons["event_join"], in: app); XCTAssertTrue(app.buttons["event_join"].isHittable)
        app.buttons["eventCategory_文化"].tap()
        reach(app.buttons["event_advice"], in: app); XCTAssertTrue(app.buttons["event_advice"].isHittable)
        app.buttons["eventCategory_经济"].tap()
        reach(app.buttons["event_v12_hongwu_registers"], in: app)
        XCTAssertTrue(app.buttons["event_v12_hongwu_registers"].isHittable)
        reach(app.buttons["category_events"], in: app); XCTAssertTrue(app.buttons["category_events"].isHittable)
    }

    @MainActor func testV11TianqiExplosionIsSocialHistory() throws {
        let app = launch(enterFamily: false)
        openEmperor("15", in: app)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["eventCategory_社会"].waitForExistence(timeout: 5))
        app.buttons["eventCategory_社会"].tap()
        reach(app.buttons["event_v11_wanggongchang_1626"], in: app)
        XCTAssertTrue(app.buttons["event_v11_wanggongchang_1626"].label.contains("王恭厂大爆炸"))
        app.buttons["event_v11_wanggongchang_1626"].tap()
        reach(app.buttons["资料与出处"], in: app, attempts: 12); app.buttons["资料与出处"].tap()
        XCTAssertTrue(app.buttons["source_v11_dpm_wanggongchang"].waitForExistence(timeout: 5))
        shot("v37-numbered-sources", app)
    }

    @MainActor func testV8KangxiSonsAndCompactHierarchy() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_q_3"], in: app, attempts: 14); app.buttons["succession_q_3"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("玄烨"))
        reach(app.buttons["allChildren"], in: app); XCTAssertTrue(app.buttons["allChildren"].label.contains("9位"))
        app.buttons["allChildren"].tap()
        for id in ["q_yinzhi_elder", "q_yinzhi_third", "q_yintang", "q_yine", "q_yinti"] {
            reach(app.buttons["member_\(id)"], in: app, attempts: 14)
            XCTAssertTrue(app.buttons["member_\(id)"].exists)
        }
        app.buttons["member_q_yinti"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("胤禵"))
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["category_relationships"].exists)
        XCTAssertTrue(app.buttons["category_records"].exists)
    }

    @MainActor func testV29ZhouTopicsOpenAsLayeredReading() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_zhou"], in: app, attempts: 8)
        app.buttons["dynasty_zhou"].tap()
        XCTAssertTrue(app.buttons["zhouGuideEntry"].waitForExistence(timeout: 5))
        reach(app.buttons["zhouGuideEntry"], in: app, attempts: 10)
        app.buttons["zhouGuideEntry"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["zhouGuidePage"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["zhouPeriod_春秋"].exists)
        app.buttons["zhouPeriod_春秋"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_confucius"].waitForExistence(timeout: 5))
        reach(app.buttons["zhouTopic_confucius"], in: app, attempts: 10)
        app.buttons["zhouTopic_confucius"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["eraTopic_confucius"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["仁、礼与君子"].exists)
        shot("v29-zhou-confucius", app)
    }

    @MainActor func testV37ZhouPeriodsAndExpandedTopics() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_zhou"], in: app, attempts: 8); app.buttons["dynasty_zhou"].tap()
        reach(app.buttons["zhouGuideEntry"], in: app, attempts: 12); app.buttons["zhouGuideEntry"].tap()
        app.buttons["zhouPeriod_西周"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_zhou-wu"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["zhouTopic_duke-zhou"].exists)
        app.buttons["zhouPeriod_战国"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_mencius"].waitForExistence(timeout: 5))
        reach(app.buttons["zhouTopic_shang-yang"], in: app, attempts: 12)
        XCTAssertTrue(app.buttons["zhouTopic_shang-yang"].exists)
        shot("v37-zhou-guide", app)
    }

    @MainActor func testV67ZhouGuideClosesVisibleCoverageGaps() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_zhou"], in: app, attempts: 8); app.buttons["dynasty_zhou"].tap()
        reach(app.buttons["zhouGuideEntry"], in: app, attempts: 12)
        XCTAssertTrue(app.buttons["zhouGuideEntry"].label.contains("25个专题"))
        app.buttons["zhouGuideEntry"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_duke-shao"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["zhouTopic_liwang-republic"].exists)
        app.buttons["zhouPeriod_春秋"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_qin-mugong"].waitForExistence(timeout: 5))
        reach(app.buttons["zhouTopic_wu-yue-rivalry"], in: app, attempts: 10)
        XCTAssertTrue(app.buttons["zhouTopic_wu-yue-rivalry"].exists)
        app.buttons["zhouPeriod_战国"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_suqin-zhangyi"].waitForExistence(timeout: 5))
        reach(app.buttons["zhouTopic_li-bing-dujiangyan"], in: app, attempts: 14)
        app.buttons["zhouTopic_li-bing-dujiangyan"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["eraTopic_li-bing-dujiangyan"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["活着的遗产"].exists)
        reach(app.buttons["联合国教科文组织世界遗产中心：青城山—都江堰"], in: app, attempts: 14)
        XCTAssertTrue(app.buttons["联合国教科文组织世界遗产中心：青城山—都江堰"].isHittable)
        shot("v67-zhou-dujiangyan", app)
    }

    @MainActor func testV29ZhuDiSignatureEventsStayVisible() throws {
        let app = launch(enterFamily: false)
        openEmperor("2", in: app)
        app.buttons["personHero"].tap()
        app.buttons["eventCategory_文化"].tap()
        XCTAssertTrue(app.buttons["event_v40m1_voyages_yongle"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["event_v12_yongle_dadian"].exists)
        app.buttons["eventCategory_军事"].tap()
        XCTAssertTrue(app.buttons["event_v17_yongle_mobei"].waitForExistence(timeout: 5))
        shot("v29-zhudi-events", app)
    }

    @MainActor func testV29NarrationShowsOnlyCompactMandarinVoices() throws {
        let app = launch()
        openArticle(in: app)
        app.buttons["朗读设置"].tap()
        XCTAssertTrue(app.navigationBars["朗读设置"].waitForExistence(timeout: 5))
        let voiceButtons = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "narrationVoice_"))
        XCTAssertEqual(voiceButtons.count, 0)
        XCTAssertFalse(app.staticTexts["未发现可用的中文系统声音"].exists)
        for rejected in ["Eddy", "Flo", "Grandma", "Grandpa", "Reed", "Rocko", "Sandy", "Shelley"] {
            XCTAssertFalse(app.staticTexts[rejected].exists)
        }
        XCTAssertFalse(app.staticTexts["婷婷"].exists)
        for index in 0..<voiceButtons.count {
            XCTAssertFalse(voiceButtons.element(boundBy: index).identifier.lowercased().contains("siri"))
        }
        shot("v29-narration-voices", app)
    }

    @MainActor func testV33ThoughtCollectionAndFreshFamilyTab() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(app.buttons["collectionCategory_ideas"].waitForExistence(timeout: 5))
        app.buttons["collectionCategory_ideas"].tap()
        XCTAssertTrue(app.buttons["artifact_idea_wang_yangming"].waitForExistence(timeout: 5))
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱元璋"))
        chooseChild("di", in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱棣"))
        app.tabBars.buttons["朝代"].tap()
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱元璋"))
    }

    @MainActor func testV33PersonOverviewVisual() throws {
        let app = launch()
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        shot("v33-person-overview", app)
    }

    @MainActor func testV34ExpandedFamilyAndQingSuccessionLanguage() throws {
        let app = launch()
        XCTAssertTrue(app.buttons["relative_di"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["祖先"].exists)
        XCTAssertTrue(app.staticTexts["子女"].exists)
        shot("v34-expanded-family", app)

        app.tabBars.buttons["朝代"].tap()
        reach(app.buttons["dynasty_qing"], in: app, attempts: 18)
        app.buttons["dynasty_qing"].tap()
        XCTAssertTrue(app.navigationBars.firstMatch.waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()
        shot("v34-dynasty-selection", app)

        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["relative_q_taksi"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["第8子"].exists)
        XCTAssertTrue(app.staticTexts["第14子"].exists)
        shot("v35-qing-expanded-lineage", app)

        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["successionPage_qing"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["开创后金"].exists)
        XCTAssertTrue(app.staticTexts["父子相承"].exists)
        shot("v34-qing-succession", app)
    }

    @MainActor func testV36ReadingHierarchyAndKangxiRelatedPeople() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 18)
        app.buttons["dynasty_qing"].tap()
        XCTAssertTrue(app.navigationBars.firstMatch.waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()

        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_q_3"], in: app, attempts: 14)
        shot("v36-succession-metadata", app)
        app.buttons["succession_q_3"].tap()
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.staticTexts["人物档案"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["eventCategory_政治"].exists)
        XCTAssertTrue(app.buttons["eventCategory_社会"].exists)
        shot("v36-person-overview", app)

        openArticle(in: app)
        reach(app.buttons["articleFamily"], in: app, attempts: 30)
        XCTAssertGreaterThanOrEqual(
            app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "associate_")).count,
            5
        )
        XCTAssertTrue(app.buttons["articleHeritage"].exists)
        shot("v36-article-footer", app)
    }

    @MainActor func testV38PausedNarrationSettingsAndNavigation() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["帝序"].tap()
        app.buttons["succession_0"].tap()
        app.buttons["personHero"].tap()
        openArticle(in: app)
        let toggle = app.buttons["narrationToggle"]
        app.buttons["narrationSettings"].tap()
        XCTAssertEqual(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "narrationVoice_")).count, 0)
        app.buttons["完成"].tap()
        toggle.tap()
        XCTAssertEqual(toggle.label, "暂停朗读")
        XCTAssertTrue(app.sliders["narrationProgress"].waitForExistence(timeout: 5))
        toggle.tap()
        XCTAssertEqual(toggle.label, "继续朗读")
        app.buttons["narrationSettings"].tap()
        app.buttons["narrationSpeed_舒缓"].tap()
        app.buttons["narrationSpeed_稍快"].tap()
        app.buttons["完成"].tap()
        XCTAssertEqual(toggle.label, "继续朗读")
        if app.buttons["narrationNext"].isEnabled { app.buttons["narrationNext"].tap() }
        XCTAssertEqual(toggle.label, "继续朗读")
        toggle.tap()
        XCTAssertEqual(toggle.label, "暂停朗读")
        app.sliders["narrationProgress"].adjust(toNormalizedSliderPosition: 0.6)
        XCTAssertEqual(toggle.label, "暂停朗读")
        shot("v38-paused-reader", app)
        toggle.tap()
        app.tabBars.buttons["朝代"].tap()
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(toggle.waitForExistence(timeout: 5))
        XCTAssertEqual(toggle.label, "开始朗读")
        app.navigationBars.buttons.element(boundBy: 0).tap()
        openArticle(in: app)
        XCTAssertEqual(toggle.label, "开始朗读")
    }

    @MainActor func testV38EmptyEventsOfferAvailableCategory() throws {
        let app = launch()
        app.buttons["personHero"].tap()
        reach(app.buttons["eventCategory_社会"], in: app)
        app.buttons["eventCategory_社会"].tap()
        reach(app.buttons["majorEventsAlternative"], in: app)
        XCTAssertTrue(app.staticTexts["majorEventsEmpty"].label.contains("社会"))
        XCTAssertFalse(app.buttons["category_events"].exists)
        shot("v38-empty-events", app)
        app.buttons["majorEventsAlternative"].tap()
        XCTAssertGreaterThan(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "event_")).count, 0)
        XCTAssertFalse(app.staticTexts["majorEventsEmpty"].exists)
    }

    @MainActor func testV38CollectionHeadingsAndSourceFooter() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap()
        shot("v38-collection", app)
        app.buttons["collectionCategory_ideas"].tap()
        app.buttons["artifact_idea_wang_yangming"].tap()
        XCTAssertTrue(app.staticTexts["思想与变革"].exists)
        XCTAssertTrue(app.staticTexts["理解线索"].exists)
        XCTAssertFalse(app.staticTexts["器物与典籍"].exists)
        shot("v38-idea-detail", app)
        let sources = app.buttons["资料与出处"]
        reach(sources, in: app)
        sources.tap()
        let links = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_"))
        XCTAssertGreaterThan(links.count, 0)
        let last = links.element(boundBy: links.count - 1)
        reach(last, in: app)
        app.swipeUp()
        XCTAssertLessThanOrEqual(last.frame.maxY, app.tabBars.firstMatch.frame.minY)
        shot("v38-source-footer", app)
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.buttons["collectionCategory_texts"].tap()
        app.buttons["artifact_v4p_famineherbal"].tap()
        XCTAssertTrue(app.staticTexts["典籍文书"].exists)
        reach(app.staticTexts["阅读线索"], in: app)
        XCTAssertTrue(app.staticTexts["阅读线索"].exists)
        shot("v38-text-detail", app)
    }


    @MainActor func openYongzhengFamily(_ large: Bool = false) -> XCUIApplication {
        let app = launch(large, enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 18)
        app.buttons["dynasty_qing"].tap()
        openEmperor("q_4", in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("胤禛"))
        return app
    }

    @MainActor func testV39YongzhengSonsAndMothers() throws {
        let app = openYongzhengFamily()
        reach(app.buttons["relative_q_ulanara"], in: app)
        shot("v39-six-consorts", app)
        for id in ["q_ulanara", "q_niuhuru", "q_lishi", "q_gengshi", "q_nianshi", "q_liushi"] {
            XCTAssertTrue(app.buttons["relative_" + id].exists)
        }
        reach(app.buttons["allChildren"], in: app)
        app.swipeUp(); shot("v39-sons-overview", app)
        app.buttons["allChildren"].tap()
        for id in ["q_honghui", "q_hongyun", "q_hongshi", "q_qianlong", "q_hongzhou", "q_hongzhan", "q_hongfen", "q_fuyi", "q_fuhui", "q_fupei"] {
            reach(app.buttons["member_" + id], in: app)
        }
        shot("v39-unranked-sons", app)
        XCTAssertLessThan(app.buttons["member_q_fupei"].frame.maxY, app.tabBars.firstMatch.frame.minY)
        app.buttons["member_q_fupei"].tap()
        reach(app.buttons["personHero"], in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("福沛"))
        XCTAssertTrue(app.buttons["relative_q_nianshi"].exists)
    }

    @MainActor func testV39HongshiReadingAndRestoredLinks() throws {
        let app = openYongzhengFamily()
        reach(app.buttons["relative_q_hongshi"], in: app)
        app.buttons["relative_q_hongshi"].tap()
        reach(app.buttons["personHero"], in: app)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        shot("v39-hongshi-overview", app)
        openArticle(in: app)
        app.buttons["articleContents"].tap()
        app.buttons["从撤去黄带到早逝"].tap()
        let links = app.buttons["chapterLinks_q_hongshi_2"]
        reach(links, in: app, attempts: 14); links.tap()
        let event = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "弘时被撤去皇子身份")).firstMatch
        reach(event, in: app); event.tap()
        XCTAssertTrue(app.staticTexts["弘时被撤去皇子身份"].waitForExistence(timeout: 5))
        shot("v39-hongshi-event", app)
    }

    @MainActor func testV39AdoptiveParentsLargeType() throws {
        let app = openYongzhengFamily(true)
        reach(app.buttons["allChildren"], in: app, attempts: 20); app.buttons["allChildren"].tap()
        reach(app.buttons["member_q_hongzhan"], in: app, attempts: 16); app.buttons["member_q_hongzhan"].tap()
        reach(app.buttons["personHero"], in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("弘曕"))
        for id in ["q_yinli", "q_yongzheng", "q_liushi"] {
            let parent = app.buttons["relative_" + id]
            reach(parent, in: app, attempts: 18)
            XCTAssertGreaterThan(parent.frame.width, 200)
            XCTAssertLessThanOrEqual(parent.frame.maxX, app.frame.maxX)
        }
        shot("v39-three-parents-large", app)
        XCTAssertTrue(app.buttons["allSiblings"].exists)
        app.buttons["relative_q_liushi"].tap()
        reach(app.buttons["personHero"], in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("刘氏"))
    }

    @MainActor func testV39YongzhengCourtChapterLinks() throws {
        let app = openYongzhengFamily()
        app.buttons["personHero"].tap()
        openArticle(in: app)
        app.buttons["articleContents"].tap(); app.buttons["有争议的继位"].tap()
        let links = app.buttons["chapterLinks_q-yongzheng-1"]
        reach(links, in: app); links.tap()
        let event = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "雍正帝即位")).firstMatch
        reach(event, in: app)
        XCTAssertTrue(event.isHittable)
        let person = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "隆科多")).firstMatch
        reach(person, in: app); person.tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        shot("v39-longkodo-overview", app)
        openArticle(in: app)
        app.buttons["articleContents"].tap(); app.buttons["荣宠消退之后"].tap()
        shot("v39-longkodo-reading", app)
    }

    @MainActor func testV39CourtRelationshipsAndHongzhou() throws {
        let app = openYongzhengFamily()
        app.buttons["personHero"].tap()
        openAssociates(in: app)
        let brother = app.buttons["associate_q_yinti"]
        reach(brother, in: app)
        XCTAssertTrue(brother.label.contains("同母弟"))
        for id in ["q_zhangtingyu", "q_eertai", "q_niangengyao", "q_longkodo"] {
            reach(app.buttons["associate_" + id], in: app)
        }
        shot("v39-court-connections", app)
        app.buttons["associate_q_zhangtingyu"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        openArticle(in: app)
        shot("v39-zhangtingyu-reading", app)
        app.terminate()

        let fresh = openYongzhengFamily()
        reach(fresh.buttons["relative_q_hongzhou"], in: fresh)
        fresh.buttons["relative_q_hongzhou"].tap()
        XCTAssertTrue(fresh.buttons["relative_q_gengshi"].waitForExistence(timeout: 5))
        fresh.buttons["personHero"].tap()
        reach(fresh.buttons["category_records"], in: fresh); fresh.buttons["category_records"].tap()
        XCTAssertTrue(fresh.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "1770")).firstMatch.exists)
        shot("v39-hongzhou-records", fresh)
    }

    @MainActor func testV40EveryEmperorHasReignPeople() throws {
        continueAfterFailure = false
        let app = launch(enterFamily: false)
        for dynasty in ["ming", "qing"] {
            if dynasty == "qing" {
                app.tabBars.buttons["朝代"].tap()
                reach(app.buttons["dynasty_qing"], in: app, attempts: 20)
                app.buttons["dynasty_qing"].tap()
            }
            app.tabBars.buttons["帝序"].tap()
            if dynasty == "qing" { XCTAssertTrue(app.buttons["succession_q_0"].isHittable) }
            let sequences = dynasty == "ming" ? (0...16).filter { $0 != 7 }.map(String.init) : (0...11).map { "q_\($0)" }
            for sequence in sequences {
                let row = app.buttons["succession_" + sequence]
                reach(row, in: app, attempts: 18); row.tap()
                XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
                app.buttons["personHero"].tap()
                let court = app.buttons["category_court"]
                XCTAssertTrue(court.waitForExistence(timeout: 5), sequence)
                reach(court, in: app); court.tap()
                XCTAssertTrue(app.navigationBars["当朝人物"].waitForExistence(timeout: 5))
                XCTAssertGreaterThanOrEqual(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "court_")).count, 2, sequence)
                if ["3", "9", "14", "q_2", "q_6", "q_10", "q_11"].contains(sequence) { shot("v40-court-" + sequence, app) }
                for _ in 0..<3 { app.navigationBars.buttons.element(boundBy: 0).tap() }
            }
        }
    }

    @MainActor func testV40ShortReignKeepsEarlierLifeSeparate() throws {
        let app = launch(enterFamily: false)
        openEmperor("14", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["eventCategory_政治"], in: app); app.buttons["eventCategory_政治"].tap()
        reach(app.buttons["category_events"], in: app); app.buttons["category_events"].tap()
        XCTAssertTrue(app.staticTexts["eventTimeScope"].label.contains("1620"))
        XCTAssertFalse(app.buttons["event_v2l_crown"].exists)
        XCTAssertFalse(app.buttons["event_v2l_tingji"].exists)
        let earlier = app.buttons["lifetimeEvents"]
        reach(earlier, in: app, attempts: 12)
        shot("v40-taichang-reign-events", app)
        earlier.tap()
        XCTAssertTrue(app.navigationBars["生平相关事件"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["eventTimeScope"].label.contains("生平"))
        reach(app.buttons["event_v2l_crown"], in: app)
        XCTAssertTrue(app.buttons["event_v2l_tingji"].exists)
        shot("v40-taichang-life-events", app)
    }

    @MainActor func testV40XuantongExcludesManchukuoFromReign() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 20); app.buttons["dynasty_qing"].tap()
        openEmperor("q_11", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["eventCategory_政治"], in: app); app.buttons["eventCategory_政治"].tap()
        reach(app.buttons["category_events"], in: app); app.buttons["category_events"].tap()
        XCTAssertFalse(app.buttons["event_qev_manchukuo_1932"].exists)
        let lifetime = app.buttons["lifetimeEvents"]
        reach(lifetime, in: app); lifetime.tap()
        XCTAssertTrue(app.navigationBars["生平相关事件"].waitForExistence(timeout: 5))
        reach(app.buttons["event_qev_manchukuo_1932"], in: app, attempts: 14)
        shot("v40-xuantong-life-events", app)
    }

    @MainActor func testV40LargeTypeCourtToPersonAndArticle() throws {
        let app = launch(true, enterFamily: false)
        openEmperor("3", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        let person = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "court_")).firstMatch
        reach(person, in: app); shot("v40-court-large", app); person.tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v40-court-article-large", app)
    }
    @MainActor func testV40QingPersonChapterEventAndSources() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 20); app.buttons["dynasty_qing"].tap()
        openEmperor("q_7", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        reach(app.buttons["court_q_linzexu"], in: app); app.buttons["court_q_linzexu"].tap()
        openArticle(in: app)
        app.buttons["articleContents"].tap(); app.buttons["广东禁烟与战争转折"].tap()
        let links = app.buttons["chapterLinks_v40q_linzexu_2"]
        reach(links, in: app, attempts: 14); links.tap()
        let event = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "林则徐主持虎门销烟")).firstMatch
        reach(event, in: app); event.tap()
        XCTAssertTrue(app.staticTexts["林则徐主持虎门销烟"].waitForExistence(timeout: 5))
        shot("v40-humen-event", app)
        let sources = app.buttons["资料与出处"]
        reach(sources, in: app, attempts: 14); sources.tap()
        let source = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).firstMatch
        reach(source, in: app); app.swipeUp()
        XCTAssertTrue(source.isHittable)
        XCTAssertLessThanOrEqual(source.frame.maxY, app.tabBars.firstMatch.frame.minY)
        shot("v40-humen-source-footer", app)
    }

    @MainActor func testV41ThoughtTopicLinksToItsAuthor() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap(); app.buttons["collectionCategory_ideas"].tap()
        app.buttons["artifact_idea_wang_yangming"].tap()
        let author = app.buttons["explore_m40_wangshouren"]
        reach(author, in: app, attempts: 14); shot("v41-yangming-topic-people", app); author.tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v41-yangming-author-reader", app)
    }

    @MainActor func testV41MedicalTextToAuthor() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap(); app.buttons["collectionCategory_texts"].tap()
        let book = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label CONTAINS %@", "artifact_", "本草纲目")).firstMatch
        reach(book, in: app, attempts: 18); book.tap()
        shot("v41-bencao-text", app)
        let author = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label CONTAINS %@", "explore_", "李时珍")).firstMatch
        reach(author, in: app, attempts: 14); author.tap()
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v41-lishizhen-reader", app)
        let articleHeritage = app.buttons["articleHeritage"]
        reach(articleHeritage, in: app, attempts: 20)
        XCTAssertTrue(articleHeritage.label.contains("相关遗珍"))
        XCTAssertFalse(articleHeritage.label.contains("陵寝"))
        shot("v42-author-article-footer", app)
        app.navigationBars.buttons.element(boundBy: 0).tap()
        let heritage = app.buttons["category_remains"]
        reach(heritage, in: app)
        XCTAssertTrue(heritage.label.contains("相关遗珍"))
        XCTAssertFalse(heritage.label.contains("陵寝"))
        heritage.tap()
        let relatedBook = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label CONTAINS %@", "personObject_", "本草纲目")).firstMatch
        reach(relatedBook, in: app); relatedBook.tap()
        shot("v41-lishizhen-back-to-book", app)
        let sources = app.buttons["资料与出处"]
        reach(sources, in: app, attempts: 14); sources.tap()
        let entries = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_"))
        XCTAssertGreaterThan(entries.count, 0)
        let lastSource = entries.element(boundBy: entries.count - 1)
        reach(lastSource, in: app, attempts: 16); app.swipeUp()
        XCTAssertLessThanOrEqual(lastSource.frame.maxY, app.tabBars.firstMatch.frame.minY)
        shot("v41-bencao-source-footer", app)
    }

    @MainActor func testV41ExpandedQingCourtToNavalFigure() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 20); app.buttons["dynasty_qing"].tap()
        openEmperor("q_10", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        let person = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label CONTAINS %@", "court_", "丁汝昌")).firstMatch
        reach(person, in: app, attempts: 16); shot("v41-guangxu-expanded-court", app); person.tap()
        openArticle(in: app); shot("v41-dingruchang-reader", app)
    }

    @MainActor func testV41LargeTypeReformTopicToLiang() throws {
        let app = launch(true, enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 25); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["遗珍"].tap()
        reach(app.buttons["collectionCategory_ideas"], in: app); app.buttons["collectionCategory_ideas"].tap()
        reach(app.buttons["artifact_idea_qing_reform"], in: app, attempts: 16); app.buttons["artifact_idea_qing_reform"].tap()
        let person = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label CONTAINS %@", "explore_", "梁启超")).firstMatch
        reach(person, in: app, attempts: 24); shot("v41-liang-topic-large", app); person.tap()
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v41-liang-reader-large", app)
    }

    @MainActor func reachReadingLink(_ element: XCUIElement, in app: XCUIApplication) {
        for _ in 0..<24 {
            if element.isHittable { return }
            let above = element.exists && element.frame.midY < app.frame.height * 0.3
            let start = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: above ? 0.4 : 0.65))
            let end = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: above ? 0.65 : 0.4))
            start.press(forDuration: 0.05, thenDragTo: end)
        }
        XCTAssertTrue(element.isHittable)
    }

    @MainActor func testV42HongzhiScholarAndChapterEvent() throws {
        let app = launch(enterFamily: false)
        openEmperor("9", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        let person = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label CONTAINS %@", "court_", "丘濬")).firstMatch
        reach(person, in: app, attempts: 16); shot("v42-hongzhi-court", app); person.tap()
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v42-qiu-reader", app)
        let links = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "chapterLinks_")).firstMatch
        reachReadingLink(links, in: app); links.tap()
        let event = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "大藤峡战争")).firstMatch
        reachReadingLink(event, in: app); event.tap()
        let sources = app.buttons["资料与出处"]
        reach(sources, in: app, attempts: 16); sources.tap()
        let entries = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_"))
        XCTAssertGreaterThan(entries.count, 0)
        let last = entries.element(boundBy: entries.count - 1)
        reach(last, in: app, attempts: 16); app.swipeUp()
        XCTAssertLessThanOrEqual(last.frame.maxY, app.tabBars.firstMatch.frame.minY)
        shot("v42-ming-event-sources", app)
    }

    @MainActor func testV42KangxiRiverOfficialsLargeType() throws {
        let app = launch(true, enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 25); app.buttons["dynasty_qing"].tap()
        openEmperor("q_3", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["category_court"], in: app, attempts: 16); app.buttons["category_court"].tap()
        let person = app.buttons["court_q_jinfu"]
        reach(person, in: app, attempts: 20); shot("v42-kangxi-court-large", app); person.tap()
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v42-jinfu-reader-large", app)
    }

    @MainActor func testV42JiaqingHasSongyun() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 20); app.buttons["dynasty_qing"].tap()
        openEmperor("q_6", in: app); app.buttons["personHero"].tap()
        reach(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        let person = app.buttons["court_q_songyun"]
        reach(person, in: app, attempts: 16); shot("v42-jiaqing-court", app); person.tap()
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v42-songyun-reader", app)
        let chapter = app.buttons["chapterLinks_v42q_songyun_2"]
        reachReadingLink(chapter, in: app); chapter.tap()
        let event = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "松筠推动伊犁开渠与旗屯试种")).firstMatch
        reachReadingLink(event, in: app); event.tap()
        XCTAssertTrue(app.buttons["资料与出处"].waitForExistence(timeout: 5))
        shot("v42-ili-canals-event", app)
    }

    @MainActor func selectDynastyV43(_ id: String, in app: XCUIApplication) {
        let button = app.buttons["dynasty_" + id]
        reachReadingLink(button, in: app); button.tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyDetail_" + id].waitForExistence(timeout: 5))
    }

    @MainActor func testV43NewDynastiesHaveWorkingTabsAndPersist() throws {
        let values = [("tang", "t_0", "唐朝帝序"), ("song_liao_xia_jin", "s_0", "宋代帝序"), ("yuan", "y_0", "元朝帝序")]
        for (dynasty, first, title) in values {
            let app = launch(enterFamily: false)
            selectDynastyV43(dynasty, in: app)
            let entry = app.buttons["dynastySequence_" + dynasty]
            reachReadingLink(entry, in: app); shot("v43-overview-" + dynasty, app); entry.tap()
            XCTAssertTrue(app.navigationBars[title].waitForExistence(timeout: 5))
            XCTAssertTrue(app.buttons["succession_" + first].exists)
            shot("v43-sequence-" + dynasty, app)
            app.tabBars.buttons["家族"].tap()
            XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
            shot("v43-family-" + dynasty, app)
            app.tabBars.buttons["遗珍"].tap()
            XCTAssertGreaterThan(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "collectionCategory_")).count, 0)
            shot("v43-collection-" + dynasty, app)
            if dynasty == "yuan" { XCTAssertFalse(app.buttons["collectionCategory_tombs"].exists) }
            XCTAssertEqual(app.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
            app.terminate()
        }
        let persisted = XCUIApplication(); persisted.launchArguments = []; persisted.launch()
        persisted.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(persisted.buttons["succession_y_0"].waitForExistence(timeout: 5))
        XCTAssertFalse(persisted.buttons["succession_0"].exists)
    }

    @MainActor func testV43TangRestorationsAndWuZhouReader() throws {
        let app = launch(enterFamily: false)
        selectDynastyV43("tang", in: app); app.tabBars.buttons["帝序"].tap()
        reachReadingLink(app.buttons["succession_t_3"], in: app)
        XCTAssertEqual(app.staticTexts["successionEra_t_3"].label, "年号 嗣圣")
        reachReadingLink(app.buttons["succession_t_6"], in: app)
        XCTAssertEqual(app.staticTexts["successionEra_t_6"].label, "年号 神龙、景龙")
        reachReadingLink(app.buttons["succession_t_5"], in: app)
        XCTAssertTrue(app.staticTexts["successionReign_t_5"].label.contains("武周"))
        XCTAssertEqual(app.staticTexts["successionTemple_t_5"].label, "无庙号")
        shot("v43-wuzhou-restorations", app)
        app.buttons["succession_t_5"].tap(); app.buttons["personHero"].tap()
        reachReadingLink(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        XCTAssertGreaterThanOrEqual(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "court_")).count, 2)
        shot("v43-wuzhou-people", app)
        app.navigationBars.buttons.element(boundBy: 0).tap(); openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v43-wuzhou-reader", app)
    }

    @MainActor func testV45TangAndSongImperialPortraits() throws {
        let tang = launch(enterFamily: false)
        let tangDynasty = tang.buttons["dynasty_tang"]
        reachReadingLink(tangDynasty, in: tang); tangDynasty.tap()
        tang.navigationBars.buttons.element(boundBy: 0).tap()
        tang.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(tang.buttons["succession_t_0"].waitForExistence(timeout: 5))
        shot("v45-tang-sequence-portraits", tang)
        tang.buttons["succession_t_0"].tap()
        XCTAssertTrue(tang.buttons["personHero"].label.contains("后世宫廷像"))
        tang.buttons["personHero"].tap()
        XCTAssertTrue(tang.buttons["portraitEntry"].waitForExistence(timeout: 5))
        tang.buttons["portraitEntry"].tap()
        XCTAssertTrue(tang.staticTexts["后世宫廷像"].waitForExistence(timeout: 5))
        shot("v45-tang-gaozu-portrait", tang)
        tang.terminate()

        let song = launch(enterFamily: false)
        let songDynasty = song.buttons["dynasty_song_liao_xia_jin"]
        reachReadingLink(songDynasty, in: song); songDynasty.tap()
        song.navigationBars.buttons.element(boundBy: 0).tap()
        song.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(song.buttons["succession_s_0"].waitForExistence(timeout: 5))
        shot("v45-song-sequence-portraits", song)
        song.buttons["succession_s_0"].tap()
        XCTAssertTrue(song.buttons["personHero"].label.contains("南薰殿旧藏"))
        song.buttons["personHero"].tap()
        XCTAssertTrue(song.buttons["portraitEntry"].waitForExistence(timeout: 5))
        song.buttons["portraitEntry"].tap()
        XCTAssertTrue(song.staticTexts["南薰殿旧藏"].waitForExistence(timeout: 5))
        shot("v45-song-taizu-portrait", song)
    }

    @MainActor func testV43SongAdoptiveFatherAndParallelRuler() throws {
        let app = launch(enterFamily: false)
        selectDynastyV43("song_liao_xia_jin", in: app)
        openEmperor("s_10", in: app)
        shot("v43-song-adoption", app)
        let adoptive = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "嗣父")).firstMatch
        XCTAssertTrue(adoptive.exists)
        app.buttons["personHero"].tap()
        reachReadingLink(app.buttons["category_relationships"], in: app); app.buttons["category_relationships"].tap()
        XCTAssertTrue(app.buttons["parent_s_gaozong"].exists)
        XCTAssertTrue(app.buttons["parent_s_gaozong"].label.contains("嗣父"))
        shot("v43-song-parent-records", app)
        app.buttons["parent_s_gaozong"].tap()
        reachReadingLink(app.buttons["category_relationships"], in: app); app.buttons["category_relationships"].tap()
        reachReadingLink(app.buttons["allChildren"], in: app); app.buttons["allChildren"].tap()
        let son = app.buttons["member_s_xiaozong"]
        XCTAssertTrue(son.waitForExistence(timeout: 5))
        XCTAssertTrue(son.label.contains("嗣子"))
        shot("v43-song-adopted-son", app)
        let fresh = launch(enterFamily: false)
        selectDynastyV43("song_liao_xia_jin", in: fresh); openEmperor("s_2", in: fresh); fresh.buttons["personHero"].tap()
        reachReadingLink(fresh.buttons["category_court"], in: fresh); fresh.buttons["category_court"].tap()
        let ruler = fresh.buttons["court_s_liao_shengzong"]
        reachReadingLink(ruler, in: fresh); ruler.tap(); openArticle(in: fresh)
        XCTAssertEqual(fresh.buttons["narrationToggle"].label, "开始朗读")
        shot("v43-liao-contemporary-reader", fresh)
    }

    @MainActor func testV43YuanLargeTypeAndShortReign() throws {
        let app = launch(true, enterFamily: false)
        selectDynastyV43("yuan", in: app); openEmperor("y_0", in: app); app.buttons["personHero"].tap()
        openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v43-kublai-reader-large", app)
        let links = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "chapterLinks_")).firstMatch
        reachReadingLink(links, in: app); links.tap(); shot("v43-yuan-chapter-links-large", app)
        let fresh = launch(enterFamily: false)
        selectDynastyV43("yuan", in: fresh); openEmperor("y_10", in: fresh); fresh.buttons["personHero"].tap()
        reachReadingLink(fresh.buttons["category_court"], in: fresh); fresh.buttons["category_court"].tap()
        XCTAssertGreaterThanOrEqual(fresh.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "court_")).count, 2)
        shot("v43-yuan-short-reign", fresh)
    }

    @MainActor func testV43MingQingThoughtAuthorsAndSources() throws {
        let app = launch(enterFamily: false)
        selectDynastyV43("qing", in: app); app.tabBars.buttons["遗珍"].tap()
        app.buttons["collectionCategory_ideas"].tap()
        let topic = app.buttons["artifact_idea_qing_jingshi"]
        reachReadingLink(topic, in: app); topic.tap()
        let author = app.buttons["explore_q_huangzongxi"]
        reachReadingLink(author, in: app); shot("v43-qing-thought-authors", app); author.tap(); openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v43-huangzongxi-reader", app)
        let chapter = app.buttons["chapterLinks_q_huangzongxi_2"]
        reachReadingLink(chapter, in: app); chapter.tap()
        let event = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "《明夷待访录》的政治追问")).firstMatch
        reachReadingLink(event, in: app); event.tap()
        let sources = app.buttons["资料与出处"]
        reachReadingLink(sources, in: app); sources.tap()
        let source = app.buttons["source_v43mq_mingyi"]
        reachReadingLink(source, in: app); app.swipeUp()
        XCTAssertLessThanOrEqual(source.frame.maxY, app.tabBars.firstMatch.frame.minY)
        shot("v43-mingyi-sources", app)
    }

    @MainActor func testV43QingAdoptedSonUsesRelationshipLabel() throws {
        let app = openYongzhengFamily()
        reachReadingLink(app.buttons["relative_q_hongzhan"], in: app); app.buttons["relative_q_hongzhan"].tap()
        reachReadingLink(app.buttons["relative_q_yinli"], in: app); app.buttons["relative_q_yinli"].tap()
        let child = app.buttons["relative_q_hongzhan"]
        reachReadingLink(child, in: app)
        XCTAssertTrue(child.label.hasPrefix("嗣子"))
        XCTAssertFalse(child.label.hasPrefix("第6子"))
        shot("v43-qing-adopted-son", app)
    }

    @MainActor func testV43TangLiteratureAndTranslation() throws {
        for (object, person) in [("v43t_jiangjinjiu_object", "t_libai"), ("v43t_xiyuji_object", "t_xuanzang")] {
            let app = launch(enterFamily: false)
            selectDynastyV43("tang", in: app); app.tabBars.buttons["遗珍"].tap()
            app.buttons["collectionCategory_texts"].tap()
            let topic = app.buttons["artifact_" + object]
            reachReadingLink(topic, in: app); topic.tap()
            let author = app.buttons["explore_" + person]
            reachReadingLink(author, in: app); shot("v43-topic-" + person, app); author.tap()
            openArticle(in: app)
            XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
            shot("v43-reader-" + person, app)
            app.terminate()
        }
    }

    @MainActor func testV43ExpandedHeritageSources() throws {
        let topics = [("song_liao_xia_jin", "texts", "v43s_mengxi"), ("yuan", "ideas", "v43y_phagpa_letters"), ("tang", "objects", "v43t_gold_tablet")]
        for (dynasty, category, object) in topics {
            let app = launch(enterFamily: false)
            selectDynastyV43(dynasty, in: app); app.tabBars.buttons["遗珍"].tap()
            app.buttons["collectionCategory_" + category].tap()
            let topic = app.buttons["artifact_" + object]
            reachReadingLink(topic, in: app); topic.tap()
            shot("v43-heritage-" + object, app)
            let disclosure = app.buttons["资料与出处"]
            reachReadingLink(disclosure, in: app); disclosure.tap()
            let source = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).firstMatch
            reachReadingLink(source, in: app); app.swipeUp()
            XCTAssertTrue(source.exists)
            XCTAssertLessThanOrEqual(source.frame.maxY, app.tabBars.firstMatch.frame.minY)
            shot("v43-heritage-sources-" + object, app)
            app.terminate()
        }
    }

    @MainActor func testV44ReaderFooterHasNoEmptyExploration() throws {
        let app = launch()
        app.buttons["personHero"].tap()
        reachReadingLink(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        reachReadingLink(app.buttons["court_lishanzhang"], in: app); app.buttons["court_lishanzhang"].tap()
        openArticle(in: app)
        app.buttons["articleContents"].tap(); app.buttons["史书里也留下了质问"].tap()
        for _ in 0..<5 { app.swipeUp() }
        XCTAssertFalse(app.staticTexts["继续探索"].exists)
        let sources = app.buttons["资料与出处"]
        XCTAssertTrue(sources.isHittable)
        XCTAssertLessThanOrEqual(sources.frame.maxY, app.buttons["narrationToggle"].frame.minY)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v44-round1-reader-footer", app)
        sources.tap()
        let source = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).firstMatch
        reachReadingLink(source, in: app); app.swipeUp()
        XCTAssertGreaterThanOrEqual(source.frame.height, 44 - 0.01)
        XCTAssertLessThanOrEqual(source.frame.maxY, app.buttons["narrationToggle"].frame.minY)
        shot("v44-round3-source-touch-target", app)
    }

    @MainActor func testV44OpeningResetsProgressAndNarration() throws {
        let app = launch(); openArticle(in: app)
        let menu = app.buttons["articleContents"]
        menu.tap(); app.buttons["1368年为什么值得单独记住"].tap()
        XCTAssertEqual(menu.value as? String, "1368年为什么值得单独记住")
        app.buttons["narrationToggle"].tap()
        XCTAssertEqual(app.buttons["narrationToggle"].label, "暂停朗读")
        menu.tap(); app.buttons["开篇"].tap()
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        XCTAssertEqual(menu.value as? String, "开篇")
        shot("v44-round2-opening", app)
        app.navigationBars.buttons.element(boundBy: 0).tap(); openArticle(in: app)
        XCTAssertEqual(menu.value as? String, "开篇")
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        app.buttons["narrationToggle"].tap()
        XCTAssertTrue(app.buttons["narrationPrevious"].waitForExistence(timeout: 5))
        XCTAssertFalse(app.buttons["narrationPrevious"].isEnabled)
        XCTAssertEqual(menu.value as? String, "一场饥荒之后")
        app.tabBars.buttons["朝代"].tap(); app.tabBars.buttons["家族"].tap(); openArticle(in: app)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v44-round2-no-autoplay", app)
    }

    @MainActor func testV44LargeReaderSourcesAndDisabledControls() throws {
        let app = launch(true)
        app.buttons["personHero"].tap()
        reachReadingLink(app.buttons["category_court"], in: app); app.buttons["category_court"].tap()
        reachReadingLink(app.buttons["court_lishanzhang"], in: app); app.buttons["court_lishanzhang"].tap()
        openArticle(in: app)
        app.buttons["articleContents"].tap(); app.buttons["开篇"].tap()
        XCTAssertFalse(app.buttons["narrationPrevious"].isEnabled)
        XCTAssertFalse(app.buttons["narrationNext"].isEnabled)
        XCTAssertEqual(app.buttons["narrationToggle"].value as? String, "在战场背后组织胜利")
        shot("v44-round3-large-reader", app)
        app.buttons["articleContents"].tap()
        reachReadingLink(app.buttons["史书里也留下了质问"], in: app)
        shot("v44-round3-large-contents", app)
        app.buttons["史书里也留下了质问"].tap()
        let sources = app.buttons["资料与出处"]
        reachReadingLink(sources, in: app); sources.tap()
        let links = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_"))
        let last = links.element(boundBy: links.count - 1)
        reachReadingLink(last, in: app); app.swipeUp()
        XCTAssertGreaterThanOrEqual(last.frame.height, 44 - 0.01)
        XCTAssertLessThanOrEqual(last.frame.maxY, app.buttons["narrationToggle"].frame.minY)
        XCTAssertFalse(app.staticTexts["继续探索"].exists)
        shot("v44-round3-large-source-footer", app)
    }

    @MainActor func testV44PeriodEventsKeepChronologicalPlacement() throws {
        let app = launch(enterFamily: false)
        selectDynastyV43("qing", in: app); openEmperor("q_2", in: app)
        app.buttons["personHero"].tap()
        reachReadingLink(app.buttons["eventCategory_政治"], in: app); app.buttons["eventCategory_政治"].tap()
        reachReadingLink(app.buttons["category_events"], in: app); app.buttons["category_events"].tap()
        let ids = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "event_")).allElementsBoundByIndex.map(\.identifier)
        let early = try XCTUnwrap(ids.firstIndex(of: "event_v43mq_zheng_split"))
        let period = try XCTUnwrap(ids.firstIndex(of: "event_v43mq_wang_yongli"))
        let later = try XCTUnwrap(ids.firstIndex(of: "event_qev_shunzhi_regency_end_1651"))
        XCTAssertLessThan(early, period)
        XCTAssertLessThan(period, later)
        XCTAssertTrue(app.buttons["event_v43mq_wang_yongli"].label.contains("17世纪中叶"))
        shot("v44-period-event-order", app)
    }

    @MainActor func testV46ExpandedImperialReadingAcrossDynasties() throws {
        let cases = [
            ("tang", "t_18", "会昌政策既有军事面，也有社会代价"),
            ("song_liao_xia_jin", "s_13", "从史弥远执政到蒙古战争"),
            ("yuan", "y_5", "晋王体系进入中央之后")
        ]
        for (dynasty, sequence, sectionTitle) in cases {
            let app = XCUIApplication()
            app.launchArguments = ["--uitesting", "--ui-dynasty", dynasty]
            app.launch()
            XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
            openEmperor(sequence, in: app)
            app.buttons["personHero"].tap()
            openArticle(in: app)
            app.buttons["articleContents"].tap()
            let section = app.buttons[sectionTitle]
            reachReadingLink(section, in: app)
            XCTAssertTrue(section.isHittable)
            section.tap()
            XCTAssertEqual(app.buttons["articleContents"].value as? String, sectionTitle)
            shot("v46-expanded-" + dynasty, app)
            app.terminate()
        }
    }

    @MainActor func testV47SocialHistoryAndMaterialCulturePaths() throws {
        let song = XCUIApplication()
        song.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        song.launch()
        XCTAssertTrue(song.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        song.tabBars.buttons["遗珍"].tap()
        song.buttons["collectionCategory_texts"].tap()
        let yingzao = song.buttons["artifact_v47s_yingzao_book"]
        reachReadingLink(yingzao, in: song); yingzao.tap()
        let lijie = song.buttons["explore_s_lijie"]
        reachReadingLink(lijie, in: song); lijie.tap()
        openArticle(in: song)
        song.buttons["articleContents"].tap()
        let evidence = song.buttons["规范文本与真实建筑之间，仍要保留距离"]
        reachReadingLink(evidence, in: song); evidence.tap()
        XCTAssertEqual(song.buttons["articleContents"].value as? String, "规范文本与真实建筑之间，仍要保留距离")
        shot("v47-lijie-reader", song)
        song.terminate()

        let society = XCUIApplication()
        society.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        society.launch()
        XCTAssertTrue(society.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        openEmperor("s_3", in: society)
        society.buttons["personHero"].tap()
        openArticle(in: society)
        society.buttons["articleContents"].tap()
        let river = society.buttons["河患与救济，检验的是长期治理"]
        reachReadingLink(river, in: society); river.tap()
        XCTAssertEqual(society.buttons["articleContents"].value as? String, "河患与救济，检验的是长期治理")
        shot("v47-song-social-history", society)
        society.terminate()

        let yuan = XCUIApplication()
        yuan.launchArguments = ["--uitesting", "--ui-dynasty", "yuan"]
        yuan.launch()
        XCTAssertTrue(yuan.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        yuan.tabBars.buttons["遗珍"].tap()
        yuan.buttons["collectionCategory_objects"].tap()
        let blueWhite = yuan.buttons["artifact_v47y_bluewhite"]
        reachReadingLink(blueWhite, in: yuan); blueWhite.tap()
        XCTAssertTrue(yuan.staticTexts["观看提示"].waitForExistence(timeout: 5))
        shot("v47-yuan-blue-white", yuan)
        let sources = yuan.buttons["资料与出处"]
        reach(sources, in: yuan, attempts: 12); sources.tap()
        let blueWhiteSource = yuan.buttons["source_v47y_dpm_bluewhite"]
        reach(blueWhiteSource, in: yuan, attempts: 8)
        XCTAssertTrue(blueWhiteSource.isHittable)
        yuan.swipeUp()
        shot("v47-yuan-source-bottom", yuan)
    }

    @MainActor func testV48QinCompleteHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "qin"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_qin"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.buttons["succession_qin_0"].exists)
        XCTAssertTrue(sequence.buttons["succession_qin_1"].exists)
        XCTAssertFalse(sequence.staticTexts["子婴"].exists)
        XCTAssertFalse(sequence.staticTexts["庙号 始皇帝"].exists)
        shot("v48-qin-sequence", sequence)
        sequence.buttons["succession_qin_0"].tap()
        sequence.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(sequence.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: sequence)
        sequence.buttons["articleContents"].tap()
        let chapter = sequence.buttons["皇帝、郡县与可计算的帝国"]
        reachReadingLink(chapter, in: sequence); chapter.tap()
        XCTAssertEqual(sequence.buttons["articleContents"].value as? String, "皇帝、郡县与可计算的帝国")
        shot("v48-qin-shihuang-reader", sequence)
        sequence.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "qin"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_texts"].tap()
        let slips = heritage.buttons["artifact_v48q_shuihudi"]
        reachReadingLink(slips, in: heritage); slips.tap()
        XCTAssertTrue(heritage.staticTexts["观看提示"].waitForExistence(timeout: 5))
        let xi = heritage.buttons["explore_qin_xi"]
        reachReadingLink(xi, in: heritage); xi.tap()
        XCTAssertTrue(heritage.buttons["articleEntry"].waitForExistence(timeout: 5))
        shot("v48-qin-slips-to-clerk", heritage)
        heritage.terminate()

        let tomb = XCUIApplication()
        tomb.launchArguments = ["--uitesting", "--ui-dynasty", "qin"]
        tomb.launch()
        XCTAssertTrue(tomb.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        tomb.tabBars.buttons["遗珍"].tap()
        tomb.buttons["collectionCategory_tombs"].tap()
        XCTAssertTrue(tomb.buttons["tomb_qin_shihuang"].waitForExistence(timeout: 5))
        tomb.buttons["tomb_qin_shihuang"].tap()
        let sources = tomb.buttons["资料与出处"]
        reach(sources, in: tomb, attempts: 14); sources.tap()
        let lastSource = tomb.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastSource, in: tomb); tomb.swipeUp()
        XCTAssertLessThanOrEqual(lastSource.frame.maxY, tomb.tabBars.firstMatch.frame.minY)
        shot("v48-qin-tomb-sources", tomb)
    }

    @MainActor func testV49HanCompleteHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_han"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.staticTexts["这里列出实际即位的西汉与东汉皇帝。西汉前、后少帝保留称号并标明名讳争议；孺子婴未称帝，王莽所建新朝及新莽末年诸政权另见人物与事件。"].exists)
        XCTAssertTrue(sequence.buttons["succession_han_00"].exists)
        let formerShao = sequence.buttons["succession_han_02"]
        reachReadingLink(formerShao, in: sequence); XCTAssertTrue(formerShao.exists)
        let latterShao = sequence.buttons["succession_han_03"]
        reachReadingLink(latterShao, in: sequence); XCTAssertTrue(latterShao.exists)
        XCTAssertFalse(sequence.staticTexts["王莽"].exists)
        shot("v49-han-sequence-boundary", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_han_00"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        person.buttons["articleContents"].tap()
        let chapter = person.buttons["楚汉战争后的国家重建"]
        reachReadingLink(chapter, in: person); chapter.tap()
        XCTAssertEqual(person.buttons["articleContents"].value as? String, "楚汉战争后的国家重建")
        shot("v49-han-gaozu-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_texts"].tap()
        let slips = heritage.buttons["artifact_v49h_juyan_slips"]
        reachReadingLink(slips, in: heritage); slips.tap()
        XCTAssertTrue(heritage.staticTexts["观看提示"].waitForExistence(timeout: 5))
        shot("v49-han-juyan-slips", heritage)
        heritage.terminate()

        let tomb = XCUIApplication()
        tomb.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        tomb.launch()
        XCTAssertTrue(tomb.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        tomb.tabBars.buttons["遗珍"].tap()
        tomb.buttons["collectionCategory_tombs"].tap()
        let baling = tomb.buttons["tomb_han_wen"]
        reachReadingLink(baling, in: tomb); baling.tap()
        let sources = tomb.buttons["资料与出处"]
        reach(sources, in: tomb, attempts: 12); sources.tap()
        XCTAssertTrue(tomb.buttons["source_v49h_ncha_baling"].waitForExistence(timeout: 5))
        shot("v49-han-baling-source", tomb)
    }

    @MainActor func testV50SuiCompleteHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "sui"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_sui"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.buttons["succession_v50s_01"].exists)
        let yangTong = sequence.buttons["succession_v50s_05"]
        reachReadingLink(yangTong, in: sequence)
        XCTAssertTrue(yangTong.exists)
        shot("v50-sui-parallel-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "sui"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_v50s_01"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        shot("v50-sui-wendi-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "sui"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_objects"].tap()
        let bottle = heritage.buttons["artifact_v50s_obj_flat"]
        reachReadingLink(bottle, in: heritage); bottle.tap()
        XCTAssertTrue(heritage.staticTexts["观看提示"].waitForExistence(timeout: 5))
        XCTAssertTrue(heritage.buttons["explore_sui_lijingxun"].exists)
        shot("v50-sui-lijingxun-object", heritage)
    }

    @MainActor func testV51ThreeKingdomsParallelHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "three_kingdoms"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_three_kingdoms"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.descendants(matching: .any)["successionGroup_曹魏"].exists)
        XCTAssertTrue(sequence.buttons["succession_v51tk_wei01"].exists)
        let shu = sequence.descendants(matching: .any)["successionGroup_蜀汉"]
        reach(shu, in: sequence, attempts: 10)
        XCTAssertTrue(shu.exists)
        let wu = sequence.descendants(matching: .any)["successionGroup_孙吴"]
        reach(wu, in: sequence, attempts: 12)
        XCTAssertTrue(wu.exists)
        shot("v51-three-kingdoms-parallel-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "three_kingdoms"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_v51tk_wei01"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        shot("v51-caopi-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "three_kingdoms"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_texts"].tap()
        let slips = heritage.buttons["artifact_v51tk_obj_wujian"]
        reachReadingLink(slips, in: heritage); slips.tap()
        XCTAssertTrue(heritage.staticTexts["十万余枚基层行政档案"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v51tk_wujian"].waitForExistence(timeout: 5))
        shot("v51-wujian-source", heritage)
    }

    @MainActor func testV52JinParallelHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "jin"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_jin"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.descendants(matching: .any)["successionGroup_西晋"].exists)
        XCTAssertTrue(sequence.buttons["succession_v52j_west01"].exists)
        let eastern = sequence.descendants(matching: .any)["successionGroup_东晋"]
        reach(eastern, in: sequence, attempts: 10)
        XCTAssertTrue(eastern.exists)
        shot("v52-jin-parallel-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "jin"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_v52j_west01"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        shot("v52-jin-wudi-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "jin"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_texts"].tap()
        let slips = heritage.buttons["artifact_v52j_obj_wujian"]
        reachReadingLink(slips, in: heritage); slips.tap()
        XCTAssertTrue(heritage.staticTexts["纸面制度之外的基层记录"].waitForExistence(timeout: 5))
        shot("v52-jin-document", heritage)
    }

    @MainActor func testV53NorthernSouthernParallelHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "northern_southern"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_northern_southern"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.descendants(matching: .any)["successionGroup_南朝宋"].exists)
        XCTAssertTrue(sequence.buttons["succession_v53ns_seq_1_01"].exists)
        let northernWei = sequence.descendants(matching: .any)["successionGroup_北魏"]
        reach(northernWei, in: sequence, attempts: 28)
        XCTAssertTrue(northernWei.exists)
        shot("v53-northern-southern-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "northern_southern"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_v53ns_seq_1_01"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        shot("v53-liuyu-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "northern_southern"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_architecture"].tap()
        let caves = heritage.buttons["artifact_v53ns_obj_yungang"]
        reachReadingLink(caves, in: heritage); caves.tap()
        XCTAssertTrue(heritage.staticTexts["国家佛教与平城时代"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v53ns_yungang"].waitForExistence(timeout: 5))
        shot("v53-yungang-source", heritage)
    }

    @MainActor func testV54FiveDynastiesParallelHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "five_dynasties"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_five_dynasties"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.descendants(matching: .any)["successionGroup_中原五代"].exists)
        XCTAssertTrue(sequence.buttons["succession_v54_seq_1_01"].exists)
        let southernTang = sequence.descendants(matching: .any)["successionGroup_南唐"]
        reach(southernTang, in: sequence, attempts: 26)
        XCTAssertTrue(southernTang.exists)
        shot("v54-five-dynasties-parallel-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "five_dynasties"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_v54_seq_1_01"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        shot("v54-zhuwen-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "five_dynasties"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_objects"].tap()
        let painting = heritage.buttons["artifact_v54_obj_night"]
        reachReadingLink(painting, in: heritage); painting.tap()
        XCTAssertTrue(heritage.staticTexts["现存宋摹本，不能直接当作现场记录"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v54_night"].waitForExistence(timeout: 5))
        shot("v54-night-revels-source", heritage)
    }

    @MainActor func testV55SongLiaoXiaJinParallelHistoryPaths() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_song_liao_xia_jin"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.descendants(matching: .any)["successionGroup_北宋"].exists)
        let liao = sequence.descendants(matching: .any)["successionGroup_辽"]
        reach(liao, in: sequence, attempts: 34)
        XCTAssertTrue(liao.exists)
        XCTAssertTrue(sequence.buttons["succession_v55_seq_辽_01"].exists)
        shot("v55-song-liao-xia-jin-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        let target = person.buttons["succession_v55_seq_辽_01"]
        reach(target, in: person, attempts: 34); target.tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        shot("v55-liao-taizu-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_architecture"].tap()
        let mausoleums = heritage.buttons["artifact_v55_obj_xixialing"]
        reachReadingLink(mausoleums, in: heritage); mausoleums.tap()
        XCTAssertTrue(heritage.staticTexts["帝陵群归属与考古边界"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v55_xixialing"].waitForExistence(timeout: 5))
        shot("v55-western-xia-mausoleums-source", heritage)
    }

    @MainActor func testV56LiaoXiaJinPeopleAndRegencyCorrections() throws {
        let liao = XCUIApplication()
        liao.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        liao.launch()
        XCTAssertTrue(liao.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        liao.tabBars.buttons["帝序"].tap()
        let daozong = liao.buttons["succession_v55_seq_辽_08"]
        reach(daozong, in: liao, attempts: 38); daozong.tap()
        liao.buttons["personHero"].tap()
        liao.buttons["category_court"].tap()
        let guanyin = liao.buttons["court_s_liao_xiaoguanyin"]
        reach(guanyin, in: liao, attempts: 12)
        XCTAssertTrue(guanyin.exists)
        guanyin.tap()
        XCTAssertTrue(liao.staticTexts["辽道宗宣懿皇后与诗人"].waitForExistence(timeout: 5))
        openArticle(in: liao)
        XCTAssertTrue(liao.staticTexts["证据与边界"].waitForExistence(timeout: 5))
        shot("v56-xiao-guanyin-reader", liao)
        liao.terminate()

        let xia = XCUIApplication()
        xia.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        xia.launch()
        XCTAssertTrue(xia.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        xia.tabBars.buttons["帝序"].tap()
        let huizong = xia.buttons["succession_v55_seq_西夏_03"]
        reach(huizong, in: xia, attempts: 46); huizong.tap()
        xia.buttons["personHero"].tap()
        xia.buttons["category_court"].tap()
        let bigLiang = xia.buttons["court_s_xia_liangtaihou"]
        reach(bigLiang, in: xia, attempts: 12)
        XCTAssertTrue(bigLiang.exists)
        bigLiang.tap()
        XCTAssertTrue(xia.staticTexts["大梁太后"].waitForExistence(timeout: 5))
        XCTAssertTrue(xia.staticTexts["西夏惠宗朝摄政者"].exists)
        shot("v56-great-liang-regent", xia)
    }

    @MainActor func testV57ShangEvidenceBoundedLearningPath() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "shang"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_shang"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.buttons["succession_v57_shang_seq_01"].exists)
        XCTAssertTrue(sequence.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "个人在位年待考")).firstMatch.exists)
        shot("v57-shang-sequence", sequence)
        sequence.buttons["succession_v57_shang_seq_01"].tap()
        sequence.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(sequence.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: sequence)
        XCTAssertTrue(sequence.buttons["articleContents"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.staticTexts["史料边界"].exists)
        shot("v57-shang-tang-reader", sequence)
        sequence.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "shang"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_texts"].tap()
        let oracle = heritage.buttons["artifact_v57_obj_oracle"]
        reachReadingLink(oracle, in: heritage); oracle.tap()
        XCTAssertTrue(heritage.staticTexts["晚商王室占卜与记事材料群"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v57_oracle"].waitForExistence(timeout: 5))
        shot("v57-oracle-sources", heritage)
    }

    @MainActor func testV58ZhouKingsIdeasAndMaterialEvidence() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "zhou"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_zhou"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.descendants(matching: .any)["successionGroup_西周"].exists)
        XCTAssertTrue(sequence.buttons["succession_v58_zhou_seq_w_01"].exists)
        XCTAssertTrue(sequence.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "断代方案")).firstMatch.exists)
        let eastern = sequence.descendants(matching: .any)["successionGroup_东周"]
        reach(eastern, in: sequence, attempts: 18)
        XCTAssertTrue(eastern.exists)
        shot("v58-zhou-two-period-sequence", sequence)
        sequence.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "zhou"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.tabBars.buttons["帝序"].tap()
        person.buttons["succession_v58_zhou_seq_w_01"].tap()
        person.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(person.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        XCTAssertTrue(person.staticTexts["史料边界"].exists)
        shot("v58-zhou-wuwang-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "zhou"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_objects"].tap()
        let hezun = heritage.buttons["artifact_v58_obj_hezun"]
        reachReadingLink(hezun, in: heritage); hezun.tap()
        XCTAssertTrue(heritage.staticTexts["成王时期“宅兹中国”铭文"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v58_nmc_zzzg"].waitForExistence(timeout: 5))
        shot("v58-hezun-sources", heritage)
    }

    @MainActor func testV59XiaReceivedKingsAndArchaeologyBoundaries() throws {
        let sequence = XCUIApplication()
        sequence.launchArguments = ["--uitesting", "--ui-dynasty", "xia"]
        sequence.launch()
        XCTAssertTrue(sequence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(sequence.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        sequence.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(sequence.descendants(matching: .any)["successionPage_xia"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.buttons["succession_v59_xia_seq_01"].exists)
        XCTAssertTrue(sequence.staticTexts["传统王名 · 无可核年号"].exists)
        XCTAssertTrue(sequence.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "不能平均拆成个人王年")).firstMatch.exists)
        shot("v59-xia-received-sequence", sequence)
        sequence.buttons["succession_v59_xia_seq_01"].tap()
        sequence.buttons["personHero"].tap()
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            XCTAssertTrue(sequence.buttons["eventCategory_" + category].exists, category)
        }
        openArticle(in: sequence)
        XCTAssertTrue(sequence.buttons["articleContents"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequence.staticTexts["阅读传世夏王"].exists)
        XCTAssertTrue(sequence.staticTexts["结论与证据边界"].exists)
        shot("v59-yu-evidence-reader", sequence)
        sequence.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "xia"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_objects"].tap()
        let bronze = heritage.buttons["artifact_v59_obj_bronze_jue"]
        reachReadingLink(bronze, in: heritage); bronze.tap()
        XCTAssertTrue(heritage.staticTexts["目前所知很早的青铜容器"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v59_nmc_jue"].waitForExistence(timeout: 5))
        shot("v59-bronze-jue-source", heritage)
    }

    @MainActor func testV60TangCourtPeopleAndMaterialHistory() throws {
        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "tang"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(person.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        person.tabBars.buttons["帝序"].tap()
        let xuanzong = person.buttons["succession_t_9"]
        reach(xuanzong, in: person, attempts: 20); xuanzong.tap()
        person.buttons["personHero"].tap()
        person.buttons["category_court"].tap()
        let guifei = person.buttons["court_t_yang_guifei"]
        reach(guifei, in: person, attempts: 18)
        XCTAssertTrue(guifei.exists)
        guifei.tap()
        XCTAssertTrue(person.staticTexts["杨贵妃"].waitForExistence(timeout: 5))
        openArticle(in: person)
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5))
        XCTAssertTrue(person.staticTexts["资料边界与继续阅读"].exists)
        shot("v60-yang-guifei-reader", person)
        person.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "tang"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_objects"].tap()
        let horse = heritage.buttons["artifact_v60_obj_horse"]
        reachReadingLink(horse, in: heritage); horse.tap()
        XCTAssertTrue(heritage.staticTexts["何家村窖藏与宫廷舞马"].waitForExistence(timeout: 5))
        let sources = heritage.buttons["资料与出处"]
        reach(sources, in: heritage, attempts: 12); sources.tap()
        XCTAssertTrue(heritage.buttons["source_v60_sxhm_horse"].waitForExistence(timeout: 5))
        shot("v60-dancing-horse-source", heritage)
    }

    @MainActor func testV61TangTombsAndGrassrootsEvidence() throws {
        let tombs = XCUIApplication()
        tombs.launchArguments = ["--uitesting", "--ui-dynasty", "tang"]
        tombs.launch()
        XCTAssertTrue(tombs.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(tombs.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        tombs.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(tombs.buttons["collectionCategory_tombs"].waitForExistence(timeout: 5))
        tombs.buttons["collectionCategory_tombs"].tap()
        let zhaoling = tombs.buttons["v61_tomb_zhaoling"]
        reachReadingLink(zhaoling, in: tombs); zhaoling.tap()
        XCTAssertTrue(tombs.staticTexts["陵寝与历史"].waitForExistence(timeout: 5))
        XCTAssertTrue(tombs.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "主陵地宫未主动发掘")).firstMatch.exists)
        let sources = tombs.buttons["资料与出处"]
        reach(sources, in: tombs, attempts: 12); sources.tap()
        XCTAssertTrue(tombs.buttons["source_v61_shaanxi_tombs"].waitForExistence(timeout: 5))
        let lastTombSource = tombs.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastTombSource, in: tombs); tombs.swipeUp()
        XCTAssertLessThanOrEqual(lastTombSource.frame.maxY, tombs.tabBars.firstMatch.frame.minY)
        shot("v61-tang-zhaoling-source", tombs)
        tombs.terminate()

        let evidence = XCUIApplication()
        evidence.launchArguments = ["--uitesting", "--ui-dynasty", "tang"]
        evidence.launch()
        XCTAssertTrue(evidence.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        evidence.tabBars.buttons["遗珍"].tap()
        evidence.buttons["collectionCategory_texts"].tap()
        let seal = evidence.buttons["artifact_v61_obj_dunhuang_seal_calendar"]
        reachReadingLink(seal, in: evidence); seal.tap()
        XCTAssertTrue(evidence.staticTexts["县级用印与日常政务"].waitForExistence(timeout: 5))
        let evidenceSources = evidence.buttons["资料与出处"]
        reach(evidenceSources, in: evidence, attempts: 12); evidenceSources.tap()
        XCTAssertTrue(evidence.buttons["source_v61_nlc_dunhuang_admin"].waitForExistence(timeout: 5))
        let lastEvidenceSource = evidence.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastEvidenceSource, in: evidence); evidence.swipeUp()
        XCTAssertLessThanOrEqual(lastEvidenceSource.frame.maxY, evidence.tabBars.firstMatch.frame.minY)
        shot("v61-dunhuang-seal-calendar-source", evidence)
    }

    @MainActor func testV62SongImperialTombsAndEvidenceBoundaries() throws {
        let tombs = XCUIApplication()
        tombs.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        tombs.launch()
        XCTAssertTrue(tombs.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(tombs.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        tombs.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(tombs.buttons["collectionCategory_tombs"].waitForExistence(timeout: 5))
        tombs.buttons["collectionCategory_tombs"].tap()
        let yongzhao = tombs.buttons["v62_tomb_yongzhao"]
        reachReadingLink(yongzhao, in: tombs); yongzhao.tap()
        XCTAssertTrue(tombs.staticTexts["陵寝与历史"].waitForExistence(timeout: 5))
        XCTAssertTrue(tombs.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "现代复原构件")).firstMatch.exists)
        let sourceToggle = tombs.buttons["资料与出处"]
        reach(sourceToggle, in: tombs, attempts: 12); sourceToggle.tap()
        XCTAssertTrue(tombs.buttons["source_v62_gongyi_plan"].waitForExistence(timeout: 5))
        let lastTombSource = tombs.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastTombSource, in: tombs); tombs.swipeUp()
        XCTAssertLessThanOrEqual(lastTombSource.frame.maxY, tombs.tabBars.firstMatch.frame.minY)
        shot("v62-song-yongzhao-source", tombs)
        tombs.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_architecture"].tap()
        let sixTombs = heritage.buttons["artifact_v62_obj_shaoxing_group"]
        reachReadingLink(sixTombs, in: heritage); sixTombs.tap()
        XCTAssertTrue(heritage.staticTexts["攒宫与无法实现的北归"].waitForExistence(timeout: 5))
        XCTAssertTrue(heritage.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "不表示现场只有六座墓")).firstMatch.exists)
        let heritageSources = heritage.buttons["资料与出处"]
        reach(heritageSources, in: heritage, attempts: 12); heritageSources.tap()
        XCTAssertTrue(heritage.buttons["source_v62_shaoxing_six"].waitForExistence(timeout: 5))
        let lastHeritageSource = heritage.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastHeritageSource, in: heritage); heritage.swipeUp()
        XCTAssertLessThanOrEqual(lastHeritageSource.frame.maxY, heritage.tabBars.firstMatch.frame.minY)
        shot("v62-song-six-tombs-source", heritage)
    }


    @MainActor func testV63LiaoXiaJinAndYuanBurialEvidence() throws {
        let frontier = XCUIApplication()
        frontier.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        frontier.launch()
        XCTAssertTrue(frontier.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(frontier.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        frontier.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(frontier.buttons["collectionCategory_tombs"].waitForExistence(timeout: 5))
        frontier.buttons["collectionCategory_tombs"].tap()
        let xixia = frontier.buttons["v63_tomb_xixia_no3"]
        reachReadingLink(xixia, in: frontier); xixia.tap()
        XCTAssertTrue(frontier.staticTexts["陵寝与历史"].waitForExistence(timeout: 5))
        XCTAssertTrue(frontier.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "传统推测")).firstMatch.exists)
        let sourceToggle = frontier.buttons["资料与出处"]
        reach(sourceToggle, in: frontier, attempts: 12); sourceToggle.tap()
        XCTAssertTrue(frontier.buttons["source_v63_xixia_neac"].waitForExistence(timeout: 5))
        let lastFrontierSource = frontier.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastFrontierSource, in: frontier); frontier.swipeUp()
        XCTAssertLessThanOrEqual(lastFrontierSource.frame.maxY, frontier.tabBars.firstMatch.frame.minY)
        shot("v63-xixia-numbered-tomb-source", frontier)
        frontier.terminate()

        let yuan = XCUIApplication()
        yuan.launchArguments = ["--uitesting", "--ui-dynasty", "yuan"]
        yuan.launch()
        XCTAssertTrue(yuan.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        yuan.tabBars.buttons["遗珍"].tap()
        XCTAssertFalse(yuan.buttons["collectionCategory_tombs"].exists)
        yuan.buttons["collectionCategory_objects"].tap()
        let secretBurial = yuan.buttons["artifact_v63_obj_yuan_secret"]
        reachReadingLink(secretBurial, in: yuan); secretBurial.tap()
        XCTAssertTrue(yuan.staticTexts["没有确定遗址，也是一项历史结论"].waitForExistence(timeout: 5))
        XCTAssertTrue(yuan.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "不虚构忽必烈")).firstMatch.exists)
        let yuanSources = yuan.buttons["资料与出处"]
        reach(yuanSources, in: yuan, attempts: 12); yuanSources.tap()
        XCTAssertTrue(yuan.buttons["source_v63_yuan_research"].waitForExistence(timeout: 5))
        let lastYuanSource = yuan.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastYuanSource, in: yuan); yuan.swipeUp()
        XCTAssertLessThanOrEqual(lastYuanSource.frame.maxY, yuan.tabBars.firstMatch.frame.minY)
        shot("v63-yuan-secret-burial-source", yuan)
    }


    @MainActor func testV64MingQingMaterialHeritageCategories() throws {
        let ming = XCUIApplication()
        ming.launchArguments = ["--uitesting", "--ui-dynasty", "ming"]
        ming.launch()
        XCTAssertTrue(ming.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(ming.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        ming.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(ming.buttons["collectionCategory_objects"].waitForExistence(timeout: 5))
        XCTAssertTrue(ming.buttons["collectionCategory_architecture"].exists)
        ming.buttons["collectionCategory_architecture"].tap()
        let forbiddenCity = ming.buttons["artifact_v64_obj_forbidden"]
        reachReadingLink(forbiddenCity, in: ming); forbiddenCity.tap()
        XCTAssertTrue(ming.staticTexts["明代营建与清代持续改造的权力空间"].waitForExistence(timeout: 5))
        XCTAssertTrue(ming.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "并非全部保持一四二〇年原状")).firstMatch.exists)
        let mingSources = ming.buttons["资料与出处"]
        reach(mingSources, in: ming, attempts: 12); mingSources.tap()
        XCTAssertTrue(ming.buttons["source_v64_forbidden"].waitForExistence(timeout: 5))
        let lastMingSource = ming.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastMingSource, in: ming); ming.swipeUp()
        XCTAssertLessThanOrEqual(lastMingSource.frame.maxY, ming.tabBars.firstMatch.frame.minY)
        shot("v64-ming-forbidden-city-source", ming)
        ming.terminate()

        let qing = XCUIApplication()
        qing.launchArguments = ["--uitesting", "--ui-dynasty", "qing"]
        qing.launch()
        XCTAssertTrue(qing.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        qing.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(qing.buttons["collectionCategory_objects"].waitForExistence(timeout: 5))
        XCTAssertTrue(qing.buttons["collectionCategory_architecture"].exists)
        qing.buttons["collectionCategory_objects"].tap()
        let enamel = qing.buttons["artifact_v64_obj_enamel"]
        reachReadingLink(enamel, in: qing); enamel.tap()
        XCTAssertTrue(qing.staticTexts["外来材料知识与宫廷作坊试验"].waitForExistence(timeout: 5))
        XCTAssertTrue(qing.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "不能把所有粉彩瓷")).firstMatch.exists)
        let qingSources = qing.buttons["资料与出处"]
        reach(qingSources, in: qing, attempts: 12); qingSources.tap()
        XCTAssertTrue(qing.buttons["source_v64_enamel"].waitForExistence(timeout: 5))
        let lastQingSource = qing.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "source_")).allElementsBoundByIndex.last!
        reachReadingLink(lastQingSource, in: qing); qing.swipeUp()
        XCTAssertLessThanOrEqual(lastQingSource.frame.maxY, qing.tabBars.firstMatch.frame.minY)
        shot("v64-qing-enamel-source", qing)
    }

    @MainActor func testV65MingQingEconomicAndSocialHistory() throws {
        let ming = XCUIApplication()
        ming.launchArguments = ["--uitesting", "--ui-dynasty", "ming"]
        ming.launch()
        XCTAssertTrue(ming.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(ming.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        ming.tabBars.buttons["帝序"].tap()
        let wanli = ming.buttons["succession_13"]
        reach(wanli, in: ming, attempts: 20); wanli.tap()
        ming.buttons["personHero"].tap()
        ming.buttons["category_events"].tap()
        ming.buttons["eventCategory_社会"].tap()
        let urban = ming.buttons["event_v65m_urban"]
        reachReadingLink(urban, in: ming); urban.tap()
        XCTAssertTrue(ming.staticTexts["城市就业、消费与社会交往扩展"].waitForExistence(timeout: 5))
        XCTAssertTrue(ming.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "并非所有地区和家庭同步进入富裕生活")).firstMatch.exists)
        let mingSources = ming.buttons["资料与出处"]
        reach(mingSources, in: ming, attempts: 12); mingSources.tap()
        XCTAssertTrue(ming.buttons["source_v65_cssn_silver_social"].waitForExistence(timeout: 5))
        shot("v65-ming-urban-life-source", ming)
        ming.terminate()

        let qing = XCUIApplication()
        qing.launchArguments = ["--uitesting", "--ui-dynasty", "qing"]
        qing.launch()
        XCTAssertTrue(qing.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        qing.tabBars.buttons["帝序"].tap()
        let xuantong = qing.buttons["succession_q_11"]
        reach(xuantong, in: qing, attempts: 20); xuantong.tap()
        qing.buttons["personHero"].tap()
        qing.buttons["category_events"].tap()
        qing.buttons["eventCategory_社会"].tap()
        let plague = qing.buttons["event_v65q_plague"]
        reachReadingLink(plague, in: qing); plague.tap()
        XCTAssertTrue(qing.staticTexts["东北肺鼠疫与近代防疫实践"].waitForExistence(timeout: 5))
        XCTAssertTrue(qing.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "不能写成一人独自指挥整个东北")).firstMatch.exists)
        let wu = qing.buttons["explore_q_wuliande"]
        reachReadingLink(wu, in: qing); wu.tap()
        XCTAssertTrue(qing.staticTexts["伍连德"].waitForExistence(timeout: 5))
        openArticle(in: qing)
        XCTAssertTrue(qing.staticTexts["从医师到全权总医官"].waitForExistence(timeout: 5))
        XCTAssertTrue(qing.buttons["articleContents"].exists)
        shot("v65-wu-liande-reader", qing)
    }

    @MainActor func testV66WomenKnowledgeEducationAndJustice() throws {
        let ming = XCUIApplication()
        ming.launchArguments = ["--uitesting", "--ui-dynasty", "ming"]
        ming.launch()
        XCTAssertTrue(ming.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        ming.tabBars.buttons["帝序"].tap()
        let zhengde = ming.buttons["succession_10"]
        reach(zhengde, in: ming, attempts: 18); zhengde.tap()
        ming.buttons["personHero"].tap()
        ming.buttons["eventCategory_文化"].tap()
        let cases = ming.buttons["event_v66m_tan_cases"]
        reachReadingLink(cases, in: ming); cases.tap()
        XCTAssertTrue(ming.staticTexts["《女医杂言》刊行并保存女性诊疗经验"].waitForExistence(timeout: 5))
        XCTAssertTrue(ming.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "不能证明谈允贤曾任宫廷女医")).firstMatch.exists)
        let tan = ming.buttons["explore_m_tanyunxian"]
        reachReadingLink(tan, in: ming); tan.tap()
        XCTAssertTrue(ming.staticTexts["谈允贤"].waitForExistence(timeout: 5))
        openArticle(in: ming)
        XCTAssertTrue(ming.staticTexts["家传医学与女性求医处境"].waitForExistence(timeout: 5))
        XCTAssertTrue(ming.buttons["articleContents"].exists)
        shot("v66-tan-yunxian-reader", ming)
        ming.terminate()

        let qing = XCUIApplication()
        qing.launchArguments = ["--uitesting", "--ui-dynasty", "qing"]
        qing.launch()
        XCTAssertTrue(qing.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        qing.tabBars.buttons["帝序"].tap()
        let guangxu = qing.buttons["succession_q_10"]
        reach(guangxu, in: qing, attempts: 20); guangxu.tap()
        qing.buttons["personHero"].tap()
        qing.buttons["eventCategory_文化"].tap()
        let allCulture = qing.buttons["category_events"]
        reach(allCulture, in: qing, attempts: 12); allCulture.tap()
        let newspaper = qing.buttons["event_v66q_womens_journal"]
        reachReadingLink(newspaper, in: qing); newspaper.tap()
        XCTAssertTrue(qing.staticTexts["秋瑾创办《中国女报》"].waitForExistence(timeout: 5))
        XCTAssertTrue(qing.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "只出版两期")).firstMatch.exists)
        let qiu = qing.buttons["explore_q_qiujin"]
        reachReadingLink(qiu, in: qing); qiu.tap()
        XCTAssertTrue(qing.staticTexts["秋瑾"].waitForExistence(timeout: 5))
        openArticle(in: qing)
        XCTAssertTrue(qing.staticTexts["《中国女报》向谁发言"].waitForExistence(timeout: 5))
        let sources = qing.buttons["资料与出处"]
        reach(sources, in: qing, attempts: 14); sources.tap()
        let lastSource = qing.buttons["source_v66_zs_women_school"]
        reachReadingLink(lastSource, in: qing); qing.swipeUp()
        XCTAssertTrue(lastSource.exists)
        XCTAssertLessThanOrEqual(lastSource.frame.maxY, qing.tabBars.firstMatch.frame.minY)
        shot("v66-qiu-jin-sources", qing)
    }

    @MainActor func testV68YuanPeopleTradeAndEvidenceBoundaries() throws {
        let app = XCUIApplication()
        app.launchArguments = ["--uitesting", "--ui-dynasty", "yuan"]
        app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(app.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        app.tabBars.buttons["帝序"].tap()
        let kublai = app.buttons["succession_y_0"]
        reach(kublai, in: app, attempts: 20); kublai.tap()
        app.buttons["personHero"].tap()
        app.buttons["eventCategory_经济"].tap()
        let finance = app.buttons["event_v50y_ahema_finance"]
        reachReadingLink(finance, in: app); finance.tap()
        XCTAssertTrue(app.staticTexts["阿合马主持财赋与专卖"].waitForExistence(timeout: 5))
        let ahmad = app.buttons["explore_y_ahmad_fanakati"]
        reachReadingLink(ahmad, in: app); ahmad.tap()
        XCTAssertTrue(app.staticTexts["阿合马"].waitForExistence(timeout: 5))
        openArticle(in: app)
        XCTAssertTrue(app.staticTexts["为什么需要新的财源"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["articleContents"].exists)
        shot("v68-yuan-ahmad-reader", app)
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.tabBars.buttons["遗珍"].tap()
        app.buttons["collectionCategory_texts"].tap()
        let letter = app.buttons["artifact_v50y_obj_autumn_letter"]
        reachReadingLink(letter, in: app); letter.tap()
        XCTAssertTrue(app.staticTexts["元 · 家书署名与代书痕迹"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "正文实为赵孟頫代书")).firstMatch.exists)
        let sources = app.buttons["资料与出处"]
        reach(sources, in: app, attempts: 14); sources.tap()
        let source = app.buttons["source_v50y_guan_letter"]
        reachReadingLink(source, in: app); app.swipeUp()
        XCTAssertLessThanOrEqual(source.frame.maxY, app.tabBars.firstMatch.frame.minY)
        shot("v68-autumn-letter-sources", app)
    }

    @MainActor func testV69LateTangAndSongReignDepth() throws {
        let tang = XCUIApplication()
        tang.launchArguments = ["--uitesting", "--ui-dynasty", "tang"]
        tang.launch()
        XCTAssertTrue(tang.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        XCTAssertEqual(tang.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        tang.tabBars.buttons["帝序"].tap()
        let yizong = tang.buttons["succession_t_20"]
        reach(yizong, in: tang, attempts: 28); yizong.tap()
        tang.buttons["personHero"].tap()
        tang.buttons["eventCategory_军事"].tap()
        let annam = tang.buttons["event_v51t_annam_recovery"]
        reachReadingLink(annam, in: tang); annam.tap()
        XCTAssertTrue(tang.staticTexts["安南失守与高骈收复交州"].waitForExistence(timeout: 5))
        let gaopian = tang.buttons["explore_t_gaopian"]
        reachReadingLink(gaopian, in: tang); gaopian.tap()
        XCTAssertTrue(tang.staticTexts["高骈"].waitForExistence(timeout: 5))
        openArticle(in: tang)
        XCTAssertTrue(tang.staticTexts["安南收复依赖运输与协同"].waitForExistence(timeout: 5))
        shot("v69-gao-pian-reader", tang)
        tang.terminate()

        let song = XCUIApplication()
        song.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        song.launch()
        XCTAssertTrue(song.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        song.tabBars.buttons["帝序"].tap()
        let zhezong = song.buttons["succession_s_6"]
        reach(zhezong, in: song, attempts: 22); zhezong.tap()
        song.buttons["personHero"].tap()
        song.buttons["eventCategory_军事"].tap()
        let pingxia = song.buttons["event_v51s_pingxia"]
        reachReadingLink(pingxia, in: song); pingxia.tap()
        XCTAssertTrue(song.staticTexts["章楶筑平夏城并组织防御"].waitForExistence(timeout: 5))
        let zhangjie = song.buttons["explore_s_zhangjie"]
        reachReadingLink(zhangjie, in: song); zhangjie.tap()
        let articleEntry = song.buttons["articleEntry"]
        reach(articleEntry, in: song); articleEntry.tap()
        if !song.buttons["articleContents"].waitForExistence(timeout: 5) {
            song.activate()
            reach(articleEntry, in: song); articleEntry.tap()
        }
        XCTAssertTrue(song.buttons["articleContents"].waitForExistence(timeout: 5))
        XCTAssertTrue(song.staticTexts["平夏城是一套工程方案"].waitForExistence(timeout: 5))
        shot("v69-zhang-jie-reader", song)
    }

    @MainActor func testV70GlobalSearchCrossesContentTypes() throws {
        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        for tab in ["朝代", "帝序", "家族", "遗珍"] {
            heritage.tabBars.buttons[tab].tap()
            XCTAssertTrue(heritage.buttons["globalSearch"].waitForExistence(timeout: 5))
        }
        heritage.buttons["globalSearch"].tap()
        XCTAssertTrue(heritage.descendants(matching: .any)["searchIntroduction"].waitForExistence(timeout: 5))
        let search = heritage.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("营造法式")
        XCTAssertTrue(heritage.buttons["search_event_v47s_yingzao"].waitForExistence(timeout: 5))
        let object = heritage.buttons["search_object_v47s_yingzao_book"]
        reach(object, in: heritage, attempts: 10)
        shot("v70-global-search-mixed-results", heritage)
        object.tap()
        XCTAssertTrue(heritage.staticTexts["《营造法式》"].waitForExistence(timeout: 5))
        heritage.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "ming"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.buttons["globalSearch"].tap()
        let personSearch = person.searchFields.firstMatch
        XCTAssertTrue(personSearch.waitForExistence(timeout: 5)); personSearch.tap(); personSearch.typeText("高骈")
        let gaopian = person.buttons["search_person_t_gaopian"]
        XCTAssertTrue(gaopian.waitForExistence(timeout: 5))
        shot("v70-global-search-person", person)
        gaopian.tap()
        XCTAssertTrue(person.staticTexts["高骈"].waitForExistence(timeout: 5))
        XCTAssertTrue(person.staticTexts["晚唐将领"].exists)
    }

    @MainActor func testV71HanReignLinksAndLiangDowager() throws {
        let searchApp = XCUIApplication()
        searchApp.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        searchApp.launch()
        XCTAssertTrue(searchApp.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        searchApp.buttons["globalSearch"].tap()
        let search = searchApp.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("梁妠")
        let liang = searchApp.buttons["search_person_han_liangna"]
        XCTAssertTrue(liang.waitForExistence(timeout: 5)); liang.tap()
        XCTAssertTrue(searchApp.staticTexts["顺烈皇后、皇太后"].waitForExistence(timeout: 5))
        XCTAssertTrue(searchApp.buttons["articleEntry"].exists)
        searchApp.buttons["category_events"].tap()
        XCTAssertTrue(searchApp.buttons["event_v52h_liang_dowager_regency"].waitForExistence(timeout: 5))
        shot("v71-liang-dowager-events", searchApp)
        searchApp.terminate()

        let reign = XCUIApplication()
        reign.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        reign.launch()
        XCTAssertTrue(reign.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        reign.tabBars.buttons["帝序"].tap()
        let chong = reign.buttons["succession_han_20"]
        reachReadingLink(chong, in: reign); chong.tap()
        reign.buttons["personHero"].tap()
        reign.buttons["category_court"].tap()
        XCTAssertTrue(reign.buttons["court_han_liangna"].waitForExistence(timeout: 5))
        XCTAssertTrue(reign.buttons["court_han_liangji"].exists)
        XCTAssertFalse(reign.buttons["court_han_zhangheng"].exists)
        shot("v71-chong-court-corrected", reign)
    }

    @MainActor func testV72SourceProvenanceLabels() throws {
        let event = XCUIApplication()
        event.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        event.launch()
        XCTAssertTrue(event.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        event.buttons["globalSearch"].tap()
        let search = event.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("梁太后临朝")
        let result = event.buttons["search_event_v52h_liang_dowager_regency"]
        XCTAssertTrue(result.waitForExistence(timeout: 5)); result.tap()
        let sources = event.buttons["资料与出处"]
        reach(sources, in: event, attempts: 16); sources.tap()
        XCTAssertTrue(event.staticTexts["sourceProvenanceNote"].waitForExistence(timeout: 5))
        let transcript = event.staticTexts["sourceKind_v49h_houhanshu"]
        let scholarship = event.staticTexts["sourceKind_v49h_cambridge"]
        XCTAssertEqual(transcript.label, "古籍转录　zh.wikisource.org")
        XCTAssertEqual(scholarship.label, "学术研究　cambridge.org")
        reach(scholarship, in: event, attempts: 6)
        shot("v72-source-types-text-and-scholarship", event)
        event.terminate()

        let heritage = XCUIApplication()
        heritage.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        heritage.launch()
        XCTAssertTrue(heritage.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        heritage.tabBars.buttons["遗珍"].tap()
        heritage.buttons["collectionCategory_tombs"].tap()
        let baling = heritage.buttons["tomb_han_wen"]
        reachReadingLink(baling, in: heritage); baling.tap()
        let tombSources = heritage.buttons["资料与出处"]
        reach(tombSources, in: heritage, attempts: 14); tombSources.tap()
        let archaeology = heritage.staticTexts["sourceKind_v49h_ncha_baling"]
        XCTAssertTrue(archaeology.waitForExistence(timeout: 5))
        XCTAssertEqual(archaeology.label, "考古与遗产　ncha.gov.cn")
        reach(archaeology, in: heritage, attempts: 6)
        shot("v72-source-type-heritage", heritage)
    }

    @MainActor func testV73PortraitsUseVerifiedBookPages() throws {
        for (sequence, title, pageText) in [
            ("6", "《明史通俗演义》第20页绣像", "原书页题名依次为于谦、明英宗、明景帝"),
            ("16", "《明史通俗演义》第32页绣像", "原书页题名依次为熊廷弼、明怀宗、周皇后")
        ] {
            let app = launch()
            openEmperor(sequence, in: app)
            app.buttons["personHero"].tap()
            app.buttons["portraitEntry"].tap()
            XCTAssertTrue(app.staticTexts[title].waitForExistence(timeout: 5))
            shot("v73-book-page-image-" + sequence, app)
            XCTAssertTrue(app.staticTexts.matching(NSPredicate(format: "label BEGINSWITH %@", pageText)).firstMatch.exists)
            let sources = app.buttons["资料与出处"]
            reach(sources, in: app, attempts: 12); sources.tap()
            XCTAssertFalse(app.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "bilibili.com")).firstMatch.exists)
            shot("v73-book-page-source-" + sequence, app)
            app.terminate()
        }
    }

    @MainActor func testV74TerritoryMapLegendAvoidsDecorativeDots() throws {
        let app = launch(enterFamily: false)
        let dynasty = app.buttons["dynasty_song_liao_xia_jin"]
        reach(dynasty, in: app, attempts: 20); dynasty.tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyDetail_song_liao_xia_jin"].waitForExistence(timeout: 5))
        let map = app.descendants(matching: .any)["territoryMap_song_liao_xia_jin"]
        reach(map, in: app, attempts: 12)
        for region in ["jin_state", "southern_song", "western_xia"] {
            XCTAssertTrue(app.descendants(matching: .any)["mapLegend_song_liao_xia_jin_" + region].exists)
        }
        shot("v74-territory-map-text-legend", app)
    }

    @MainActor func testV75RelationshipEvidenceReadsAsChinese() throws {
        let app = launch()
        app.buttons["personHero"].tap()
        app.buttons["category_records"].tap()
        let evidence = app.buttons["亲属关系的依据"]
        reach(evidence, in: app, attempts: 10); evidence.tap()
        let father = app.staticTexts["relationEvidence_yuanzhang_father_shizhen"]
        XCTAssertTrue(father.waitForExistence(timeout: 5))
        XCTAssertEqual(father.label, "朱元璋的父亲是朱世珍")
        XCTAssertFalse(app.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "→")).firstMatch.exists)
        shot("v75-relationship-evidence-sentence", app)
    }

    @MainActor func testV76SearchExplainsTruncatedResults() throws {
        let app = launch(enterFamily: false)
        app.buttons["globalSearch"].tap()
        let search = app.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("皇帝")
        let summary = app.staticTexts["searchResultCount"]
        XCTAssertTrue(summary.waitForExistence(timeout: 5))
        XCTAssertTrue(summary.label.contains("显示相关度较高的前"))
        let peopleCount = app.staticTexts["searchSectionCount_people"]
        XCTAssertTrue(peopleCount.exists)
        XCTAssertTrue(peopleCount.label.contains("/"))
        XCTAssertFalse(app.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", " · ")).firstMatch.exists)
        shot("v76-search-total-and-visible-counts", app)
    }

    @MainActor func testV77ZhouTopicsExplainSourceTypes() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_zhou"], in: app, attempts: 8); app.buttons["dynasty_zhou"].tap()
        reach(app.buttons["zhouGuideEntry"], in: app, attempts: 12); app.buttons["zhouGuideEntry"].tap()
        app.buttons["zhouPeriod_春秋"].tap()
        reach(app.buttons["zhouTopic_confucius"], in: app, attempts: 10); app.buttons["zhouTopic_confucius"].tap()
        let note = app.staticTexts["zhouSourceProvenanceNote"]
        reach(note, in: app, attempts: 18)
        XCTAssertTrue(note.isHittable)
        XCTAssertEqual(app.staticTexts["zhouSourceKind_0"].label, "学术研究　plato.stanford.edu")
        XCTAssertEqual(app.staticTexts["zhouSourceKind_1"].label, "古籍转录　ctext.org")
        shot("v77-zhou-source-provenance", app)
    }

    @MainActor func testV78LongPagesClearTheTabBar() throws {
        let records = launch()
        records.buttons["personHero"].tap()
        records.buttons["category_records"].tap()
        let sources = records.buttons["资料与出处"]
        reach(sources, in: records, attempts: 18)
        XCTAssertLessThan(sources.frame.maxY, records.tabBars.firstMatch.frame.minY - 8)
        shot("v78-records-bottom-clearance", records)
        records.terminate()

        let portrait = launch()
        portrait.buttons["personHero"].tap()
        portrait.buttons["portraitEntry"].tap()
        let finalNote = portrait.staticTexts["历史画像未必是生前写生；作品资料及图像说明见原始出处。"]
        reach(finalNote, in: portrait, attempts: 20)
        XCTAssertLessThan(finalNote.frame.maxY, portrait.tabBars.firstMatch.frame.minY - 8)
        shot("v78-portrait-bottom-clearance", portrait)
    }

    @MainActor func testV79DynastyListEndsWithoutExcessBlankSpace() throws {
        let app = launch(enterFamily: false)
        let qing = app.buttons["dynasty_qing"]
        reach(qing, in: app, attempts: 20)
        app.swipeUp()
        let gap = app.tabBars.firstMatch.frame.minY - qing.frame.maxY
        XCTAssertGreaterThan(gap, 20)
        XCTAssertLessThan(gap, 60)
        shot("v79-dynasty-list-compact-ending", app)
    }

    @MainActor func testV80PageFamiliesUseCompactBottomSpacing() throws {
        let overview = launch(enterFamily: false)
        reach(overview.buttons["dynasty_sui"], in: overview, attempts: 10); overview.buttons["dynasty_sui"].tap()
        assertCompactPageEnding(overview.buttons["资料与出处"], in: overview)
        shot("v80-dynasty-detail-compact-ending", overview)
        overview.terminate()

        let sequence = launch(enterFamily: false)
        sequence.tabBars.buttons["帝序"].tap()
        assertCompactPageEnding(sequence.staticTexts["successionEndNote"], in: sequence, attempts: 24)
        shot("v80-sequence-compact-ending", sequence)
        sequence.terminate()

        let person = launch()
        person.buttons["personHero"].tap(); person.buttons["category_records"].tap()
        assertCompactPageEnding(person.buttons["资料与出处"], in: person)
        shot("v80-person-records-compact-ending", person)
    }

    @MainActor func testV86MingQingCentralReadingsHaveFiveLayerDepth() throws {
        for (dynasty, query, personID, chapters) in [
            ("ming", "王守仁", "m40_wangshouren", ["从科举官员到龙场贬谪", "知行合一不是成功学口号", "南赣治理中的组织与强制", "宁王之乱与军功风波", "晚年军务与学说的多重遗产"]),
            ("qing", "林则徐", "q_linzexu", ["地方治理形成的行政经验", "朝廷争论与钦差权力的边界", "虎门销烟与文献能够确认的事实", "战争失败、革职与新疆经历", "译报、世界知识与后来的记忆"])
        ] {
            let app = XCUIApplication()
            app.launchArguments = ["--uitesting", "--ui-dynasty", dynasty]
            app.launch()
            XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
            app.buttons["globalSearch"].tap()
            let search = app.searchFields.firstMatch
            XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText(query)
            let result = app.buttons["search_person_" + personID]
            XCTAssertTrue(result.waitForExistence(timeout: 5)); result.tap()
            XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5)); app.buttons["articleEntry"].tap()
            XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5)); app.buttons["articleContents"].tap()
            for chapter in chapters { XCTAssertTrue(app.buttons[chapter].exists) }
            XCTAssertTrue(app.buttons[chapters[2]].exists); app.buttons[chapters[2]].tap()
            XCTAssertTrue(app.staticTexts[chapters[2]].waitForExistence(timeout: 5))
            XCTAssertTrue(app.buttons["narrationToggle"].exists)
            if dynasty == "ming" {
                let toggle = app.buttons["narrationToggle"]
                toggle.tap()
                expectation(for: NSPredicate(format: "label == %@", "暂停朗读"), evaluatedWith: toggle)
                waitForExpectations(timeout: 30)
                XCTAssertTrue(app.sliders["narrationProgress"].waitForExistence(timeout: 5))
            }
            shot("v86-" + dynasty + "-layered-reading", app)
            app.terminate()
        }
    }

    @MainActor func testV87ContestedMingQingFiguresKeepEvidenceBoundaries() throws {
        for (dynasty, query, personID, chapters, target) in [
            ("ming", "袁崇焕", "m40_yuanchonghuan", ["文官进入辽东战场", "宁远胜利来自多年组织", "督师权限与毛文龙之死", "己巳之变与北京城下", "处刑、反间说与证据边界"], 4),
            ("qing", "梁启超", "q_liangqichao", ["从科举士人到维新作者", "《时务报》成为政治课堂", "戊戌失败后的海外转向", "《新民说》讨论公共能力", "思想变化不是简单反复"], 2)
        ] {
            let app = XCUIApplication()
            app.launchArguments = ["--uitesting", "--ui-dynasty", dynasty]
            app.launch()
            XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
            app.buttons["globalSearch"].tap()
            let search = app.searchFields.firstMatch
            XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText(query)
            let result = app.buttons["search_person_" + personID]
            XCTAssertTrue(result.waitForExistence(timeout: 5)); result.tap()
            XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5)); app.buttons["articleEntry"].tap()
            XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5)); app.buttons["articleContents"].tap()
            for chapter in chapters { XCTAssertTrue(app.buttons[chapter].exists) }
            app.buttons[chapters[target]].tap()
            XCTAssertTrue(app.staticTexts[chapters[target]].waitForExistence(timeout: 5))
            if dynasty == "ming" {
                let toggle = app.buttons["narrationToggle"]
                toggle.tap()
                expectation(for: NSPredicate(format: "label == %@", "暂停朗读"), evaluatedWith: toggle)
                waitForExpectations(timeout: 30)
                XCTAssertTrue(app.sliders["narrationProgress"].waitForExistence(timeout: 5))
            }
            shot("v87-" + dynasty + "-evidence-bounded-reading", app)
            app.terminate()
        }
    }

    @MainActor func testV88InstitutionalReadingsKeepFiveLayerDepth() throws {
        for (dynasty, query, personID, chapters, target) in [
            ("ming", "魏忠贤", "m40_weizhongxian", ["从内廷差役到皇帝近侍", "外廷冲突怎样进入内廷", "杨涟弹劾与奏疏失去安全", "诏狱、追赃与政治暴力", "崇祯清算及其有限修复"], 3),
            ("qing", "洪秀全", "q_hongxiuquan", ["科举挫折与宗教解释", "金田起义与军事共同体", "定都天京与制度试验", "性别规范与权力等级的张力", "内部分裂、天京陷落与记忆"], 2)
        ] {
            let app = XCUIApplication()
            app.launchArguments = ["--uitesting", "--ui-dynasty", dynasty]
            app.launch()
            XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
            app.buttons["globalSearch"].tap()
            let search = app.searchFields.firstMatch
            XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText(query)
            let result = app.buttons["search_person_" + personID]
            XCTAssertTrue(result.waitForExistence(timeout: 5)); result.tap()
            XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5)); app.buttons["articleEntry"].tap()
            XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5)); app.buttons["articleContents"].tap()
            for chapter in chapters { XCTAssertTrue(app.buttons[chapter].exists) }
            app.buttons[chapters[target]].tap()
            XCTAssertTrue(app.staticTexts[chapters[target]].waitForExistence(timeout: 5))
            if dynasty == "ming" {
                let toggle = app.buttons["narrationToggle"]
                XCTAssertTrue(toggle.exists); toggle.tap()
                expectation(for: NSPredicate(format: "label == %@", "暂停朗读"), evaluatedWith: toggle)
                waitForExpectations(timeout: 30)
                XCTAssertTrue(app.sliders["narrationProgress"].waitForExistence(timeout: 5))
            }
            shot("v88-" + dynasty + "-institutional-reading", app)
            app.terminate()
        }
    }

    @MainActor func testV89BeijingManIsProminentAndPrehistoryReadingsAreLayered() throws {
        let app = launch(enterFamily: false)
        XCTAssertTrue(app.buttons["dynasty_prehistory"].waitForExistence(timeout: 5)); app.buttons["dynasty_prehistory"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryPage"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["在时间中观察遗址"].exists)
        shot("v89-prehistory-overview", app)
        let beijing = app.buttons["prehistoricGuide_zhoukoudian"]
        reach(beijing, in: app, attempts: 16); XCTAssertTrue(beijing.isHittable); beijing.tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistorySiteDetail_zhoukoudian"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["北京人遗址（周口店第一地点）"].exists)
        for title in ["从龙骨山到第一颗头盖骨", "洞穴里保存了哪些证据", "石器、取食与火的讨论", "年代从五十万年推到更早", "失踪化石与仍在继续的研究", "证据如何解读"] {
            XCTAssertTrue(app.staticTexts[title].exists)
        }
        reach(app.buttons["资料与出处"], in: app, attempts: 20)
        XCTAssertTrue(app.buttons["资料与出处"].isHittable)
        shot("v89-beijing-man-layered-reading", app)
        app.terminate()

        let searchApp = launch(enterFamily: false)
        searchApp.buttons["globalSearch"].tap()
        let search = searchApp.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("北京人")
        XCTAssertTrue(searchApp.buttons["search_site_zhoukoudian"].waitForExistence(timeout: 5))
        shot("v89-beijing-man-search", searchApp)
    }

    @MainActor func testV112PrehistoryMacroReadingIsDiscoverable() throws {
        let app = launch(enterFamily: false)
        XCTAssertTrue(app.buttons["dynasty_prehistory"].waitForExistence(timeout: 5))
        app.buttons["dynasty_prehistory"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryPage"].waitForExistence(timeout: 5))

        let entry = app.buttons["prehistoryInterpretationEntry"]
        reach(entry, in: app, attempts: 12)
        XCTAssertTrue(entry.isHittable)
        shot("v112-prehistory-macro-entry", app)
        entry.tap()

        XCTAssertTrue(app.descendants(matching: .any)["prehistoryInterpretationPage"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["理解史前中国"].exists)
        XCTAssertTrue(app.staticTexts["百万年人类活动"].exists)
        shot("v112-prehistory-macro-reading-opening", app)

        let method = app.staticTexts["怎样阅读考古结论"]
        reach(method, in: app, attempts: 18)
        XCTAssertTrue(method.exists)
        reach(app.buttons["资料与出处"], in: app, attempts: 10)
        XCTAssertTrue(app.buttons["资料与出处"].isHittable)
        shot("v112-prehistory-macro-reading-ending", app)
    }

    @MainActor func testV113XiaAndShangInterpretationsAreLayered() throws {
        let app = launch(enterFamily: false)
        XCTAssertTrue(app.buttons["dynasty_xia"].waitForExistence(timeout: 5))
        app.buttons["dynasty_xia"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyDetail_xia"].waitForExistence(timeout: 5))
        let xiaEntry = app.buttons["dynastyInterpretation_xia"]
        reach(xiaEntry, in: app, attempts: 14)
        app.swipeUp()
        XCTAssertTrue(xiaEntry.isHittable)
        shot("v113-xia-interpretation-entry", app)
        xiaEntry.tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyInterpretationPage_xia"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["三层证据不能混写"].exists)
        let xiaEnding = app.staticTexts["不让传说替代人物史"]
        reach(xiaEnding, in: app, attempts: 14)
        XCTAssertTrue(xiaEnding.exists)
        reach(app.buttons["资料与出处"], in: app, attempts: 8)
        XCTAssertTrue(app.buttons["资料与出处"].isHittable)
        shot("v113-xia-interpretation-ending", app)

        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        XCTAssertTrue(app.buttons["dynasty_shang"].waitForExistence(timeout: 5))
        app.buttons["dynasty_shang"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyDetail_shang"].waitForExistence(timeout: 5))
        let shangEntry = app.buttons["dynastyInterpretation_shang"]
        reach(shangEntry, in: app, attempts: 14)
        XCTAssertTrue(shangEntry.isHittable)
        shangEntry.tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyInterpretationPage_shang"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["两种尺度的证据"].exists)
        let writing = app.staticTexts["甲骨文记录了谁的世界"]
        reach(writing, in: app, attempts: 14)
        XCTAssertTrue(writing.exists)
        shot("v113-shang-writing-perspective", app)
    }

    @MainActor func testV90ThinPeopleAndEmptyEventLensesHaveUsefulDepth() throws {
        let ming = XCUIApplication()
        ming.launchArguments = ["--uitesting", "--ui-dynasty", "ming"]
        ming.launch()
        XCTAssertTrue(ming.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        ming.buttons["globalSearch"].tap()
        let mingSearch = ming.searchFields.firstMatch
        XCTAssertTrue(mingSearch.waitForExistence(timeout: 5)); mingSearch.tap(); mingSearch.typeText("朱由校")
        XCTAssertTrue(ming.buttons["search_person_youxiao"].waitForExistence(timeout: 5)); ming.buttons["search_person_youxiao"].tap()
        reach(ming.buttons["eventCategory_经济"], in: ming, attempts: 12); ming.buttons["eventCategory_经济"].tap()
        XCTAssertTrue(ming.staticTexts["辽饷、军费与天启财政"].waitForExistence(timeout: 5))
        XCTAssertFalse(ming.staticTexts["majorEventsRelatedContext"].exists)
        shot("v90-direct-economic-history", ming)
        ming.terminate()

        let context = XCUIApplication()
        context.launchArguments = ["--uitesting", "--ui-dynasty", "ming"]
        context.launch()
        XCTAssertTrue(context.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        context.buttons["globalSearch"].tap()
        let contextSearch = context.searchFields.firstMatch
        XCTAssertTrue(contextSearch.waitForExistence(timeout: 5)); contextSearch.tap(); contextSearch.typeText("朱常洛")
        XCTAssertTrue(context.buttons["search_person_changluo"].waitForExistence(timeout: 5)); context.buttons["search_person_changluo"].tap()
        reach(context.buttons["eventCategory_军事"], in: context, attempts: 12); context.buttons["eventCategory_军事"].tap()
        XCTAssertTrue(context.staticTexts["majorEventsRelatedContext"].waitForExistence(timeout: 5))
        XCTAssertEqual(context.staticTexts["eventTimeScope"].label, "延伸阅读 · 同一历史阶段")
        XCTAssertTrue(context.staticTexts["萨尔浒战役"].exists)
        shot("v90-related-period-history", context)
        context.terminate()

        let person = XCUIApplication()
        person.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        person.launch()
        XCTAssertTrue(person.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        person.buttons["globalSearch"].tap()
        let personSearch = person.searchFields.firstMatch
        XCTAssertTrue(personSearch.waitForExistence(timeout: 5)); personSearch.tap(); personSearch.typeText("赵德芳")
        XCTAssertTrue(person.buttons["search_person_s_zhaodefang"].waitForExistence(timeout: 5)); person.buttons["search_person_s_zhaodefang"].tap()
        XCTAssertTrue(person.buttons["articleEntry"].waitForExistence(timeout: 5)); person.buttons["articleEntry"].tap()
        XCTAssertTrue(person.buttons["articleContents"].waitForExistence(timeout: 5)); person.buttons["articleContents"].tap()
        for chapter in ["先确认身份与时间", "世系中的具体位置", "为什么值得单独阅读", "材料边界", "从关系图回到历史问题"] {
            XCTAssertTrue(person.buttons[chapter].exists)
        }
        person.buttons["材料边界"].tap()
        XCTAssertTrue(person.staticTexts["材料边界"].waitForExistence(timeout: 5))
        shot("v90-formerly-thin-person-reading", person)
    }

    @MainActor func testV91PeriodContextIsNotPresentedAsPersonalAction() throws {
        let app = XCUIApplication()
        app.launchArguments = ["--uitesting", "--ui-dynasty", "tang"]
        app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        app.buttons["globalSearch"].tap()
        let search = app.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("李治")
        XCTAssertTrue(app.buttons["search_person_t_gaozong"].waitForExistence(timeout: 5)); app.buttons["search_person_t_gaozong"].tap()
        reach(app.buttons["eventCategory_经济"], in: app, attempts: 12); app.buttons["eventCategory_经济"].tap()
        XCTAssertTrue(app.staticTexts["majorEventsPeriodContext"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["eventTimeScope"].label.hasPrefix("在位时期 · 含同期背景"))
        shot("v91-period-context-disclosure", app)
    }

    @MainActor func testV96EasternHanUsesCEReignMaterial() throws {
        let app = XCUIApplication()
        app.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        app.buttons["globalSearch"].tap()
        let search = app.searchFields.firstMatch
        XCTAssertTrue(search.waitForExistence(timeout: 5)); search.tap(); search.typeText("刘秀")
        XCTAssertTrue(app.buttons["search_person_han_guangwu"].waitForExistence(timeout: 5)); app.buttons["search_person_han_guangwu"].tap()
        reach(app.buttons["eventCategory_社会"], in: app, attempts: 12); app.buttons["eventCategory_社会"].tap()
        XCTAssertTrue(app.staticTexts["释放奴婢诏令与战后社会恢复"].waitForExistence(timeout: 5))
        XCTAssertFalse(app.staticTexts["昭君出塞"].exists)
        XCTAssertFalse(app.staticTexts["majorEventsPeriodContext"].exists)
        shot("v96-eastern-han-social-history", app)
    }

    @MainActor func testV106DurableReignsAndFiveDynastiesReadingsAreDeep() throws {
        let song = XCUIApplication()
        song.launchArguments = ["--uitesting", "--ui-dynasty", "song_liao_xia_jin"]
        song.launch()
        XCTAssertTrue(song.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        song.buttons["globalSearch"].tap()
        let songSearch = song.searchFields.firstMatch
        XCTAssertTrue(songSearch.waitForExistence(timeout: 5)); songSearch.tap(); songSearch.typeText("赵恒")
        XCTAssertTrue(song.buttons["search_person_s_zhenzong"].waitForExistence(timeout: 5)); song.buttons["search_person_s_zhenzong"].tap()
        reach(song.buttons["eventCategory_社会"], in: song, attempts: 12); song.buttons["eventCategory_社会"].tap()
        XCTAssertTrue(song.staticTexts["封禅、宫观营建与地方进献"].waitForExistence(timeout: 5))
        XCTAssertFalse(song.staticTexts["majorEventsRelatedContext"].exists)
        shot("v106-song-social-history", song)
        song.terminate()

        let five = XCUIApplication()
        five.launchArguments = ["--uitesting", "--ui-dynasty", "five_dynasties"]
        five.launch()
        XCTAssertTrue(five.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        five.buttons["globalSearch"].tap()
        let fiveSearch = five.searchFields.firstMatch
        XCTAssertTrue(fiveSearch.waitForExistence(timeout: 5)); fiveSearch.tap(); fiveSearch.typeText("朱温")
        XCTAssertTrue(five.buttons["search_person_fd_zhuwen"].waitForExistence(timeout: 5)); five.buttons["search_person_fd_zhuwen"].tap()
        XCTAssertTrue(five.buttons["articleEntry"].waitForExistence(timeout: 5)); five.buttons["articleEntry"].tap()
        XCTAssertTrue(five.buttons["articleContents"].waitForExistence(timeout: 5)); five.buttons["articleContents"].tap()
        XCTAssertTrue(five.buttons["从唐末军阀到后梁皇帝"].exists)
        five.buttons["从唐末军阀到后梁皇帝"].tap()
        XCTAssertTrue(five.staticTexts["从唐末军阀到后梁皇帝"].waitForExistence(timeout: 5))
        shot("v106-five-dynasties-sixth-layer", five)
    }

    @MainActor func testV107CorrectedChronologyIsVisibleInProduct() throws {
        let qi = XCUIApplication()
        qi.launchArguments = ["--uitesting", "--ui-dynasty", "northern_southern"]
        qi.launch()
        XCTAssertTrue(qi.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        qi.buttons["globalSearch"].tap()
        let qiSearch = qi.searchFields.firstMatch
        XCTAssertTrue(qiSearch.waitForExistence(timeout: 5)); qiSearch.tap(); qiSearch.typeText("萧赜")
        XCTAssertTrue(qi.buttons["search_person_ns_qi_wu"].waitForExistence(timeout: 5)); qi.buttons["search_person_ns_qi_wu"].tap()
        reach(qi.buttons["eventCategory_社会"], in: qi, attempts: 12); qi.buttons["eventCategory_社会"].tap()
        XCTAssertTrue(qi.staticTexts["永明八年调整却籍处置"].waitForExistence(timeout: 5))
        XCTAssertFalse(qi.staticTexts["检籍、却籍与户籍冲突"].exists)
        shot("v107-qi-registration-correction", qi)
        qi.terminate()

        let han = XCUIApplication()
        han.launchArguments = ["--uitesting", "--ui-dynasty", "han"]
        han.launch()
        XCTAssertTrue(han.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        han.buttons["globalSearch"].tap()
        let hanSearch = han.searchFields.firstMatch
        XCTAssertTrue(hanSearch.waitForExistence(timeout: 5)); hanSearch.tap(); hanSearch.typeText("刘秀")
        XCTAssertTrue(han.buttons["search_person_han_guangwu"].waitForExistence(timeout: 5)); han.buttons["search_person_han_guangwu"].tap()
        reach(han.buttons["eventCategory_文化"], in: han, attempts: 12); han.buttons["eventCategory_文化"].tap()
        XCTAssertTrue(han.staticTexts["建武五年修起洛阳太学"].waitForExistence(timeout: 5))
        shot("v107-guangwu-taixue-date", han)
    }

    @MainActor func testV108ThreeKingdomsReadingsArePersonSpecific() throws {
        let sun = XCUIApplication()
        sun.launchArguments = ["--uitesting", "--ui-dynasty", "three_kingdoms"]
        sun.launch()
        XCTAssertTrue(sun.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        sun.buttons["globalSearch"].tap()
        let sunSearch = sun.searchFields.firstMatch
        XCTAssertTrue(sunSearch.waitForExistence(timeout: 5)); sunSearch.tap(); sunSearch.typeText("孙策")
        XCTAssertTrue(sun.buttons["search_person_tk_sunce"].waitForExistence(timeout: 5)); sun.buttons["search_person_tk_sunce"].tap()
        XCTAssertTrue(sun.buttons["articleEntry"].waitForExistence(timeout: 5)); sun.buttons["articleEntry"].tap()
        XCTAssertTrue(sun.buttons["articleContents"].waitForExistence(timeout: 5)); sun.buttons["articleContents"].tap()
        for chapter in ["从袁术部下到渡江自立", "江东地方精英既合作也抵抗", "比较征服与治理"] {
            XCTAssertTrue(sun.buttons[chapter].exists)
        }
        XCTAssertFalse(sun.buttons["时代位置"].exists)
        sun.buttons["江东地方精英既合作也抵抗"].tap()
        XCTAssertTrue(sun.staticTexts["江东地方精英既合作也抵抗"].waitForExistence(timeout: 5))
        shot("v108-sun-ce-specific-reading", sun)
        sun.terminate()

        let ji = XCUIApplication()
        ji.launchArguments = ["--uitesting", "--ui-dynasty", "three_kingdoms"]
        ji.launch()
        XCTAssertTrue(ji.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        ji.buttons["globalSearch"].tap()
        let jiSearch = ji.searchFields.firstMatch
        XCTAssertTrue(jiSearch.waitForExistence(timeout: 5)); jiSearch.tap(); jiSearch.typeText("嵇康")
        XCTAssertTrue(ji.buttons["search_person_tk_jikang"].waitForExistence(timeout: 5)); ji.buttons["search_person_tk_jikang"].tap()
        XCTAssertTrue(ji.buttons["articleEntry"].waitForExistence(timeout: 5)); ji.buttons["articleEntry"].tap()
        XCTAssertTrue(ji.buttons["articleContents"].waitForExistence(timeout: 5)); ji.buttons["articleContents"].tap()
        XCTAssertTrue(ji.buttons["音乐、养生与名教批评"].exists)
        XCTAssertTrue(ji.buttons["广陵散与可确认事实"].exists)
        XCTAssertTrue(ji.buttons["思想、生活与政治不能拆开"].exists)
        shot("v108-ji-kang-specific-reading", ji)
    }

}
