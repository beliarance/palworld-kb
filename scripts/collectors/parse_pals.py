#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse Palworld pal list (scraped from palworld.gg/pals, game v1.0) into CSV."""
import re, csv, os

RAW = r"""
[Dragon elementEarth elementNEWAegidronAegidron #1848EpicMining8](https://palworld.gg/pal/aegidron)
[Water elementNEWAmioneAmione #472CommonWatering1Handiwork2Transporting1](https://palworld.gg/pal/amione)
[Earth elementAnubisAnubis #13910EpicHandiwork6Mining6Transporting4](https://palworld.gg/pal/anubis)
[Fire elementArsoxArsox #584CommonKindling3Deforesting2](https://palworld.gg/pal/arsox)
[Dragon elementDark elementAstegonAstegon #1589EpicHandiwork3Mining7](https://palworld.gg/pal/astegon)
[NEWAstralymAstralym #20410Epic](https://palworld.gg/pal/astralym)
[Electricity elementAzurmaneAzurmane #1617RareGenerating Electricity5](https://palworld.gg/pal/azurmane)
[Water elementDragon elementAzurobeAzurobe #417RareWatering4](https://palworld.gg/pal/azurobe)
[Ice elementDragon elementAzurobe CrystAzurobe Cryst #41B8EpicCooling4](https://palworld.gg/pal/azurobe-cryst)
[Dark elementNEWBakemiBakemi #1684CommonHandiwork3Medicine Production4Transporting2](https://palworld.gg/pal/bakemi)
[Ice elementBastigorBastigor #1918EpicDeforesting6Mining5Cooling8](https://palworld.gg/pal/bastigor)
[Electricity elementBeakonBeakon #966RareGenerating Electricity4Gathering2Transporting5](https://palworld.gg/pal/beakon)
[Ice elementNEWBeakon CrystBeakon Cryst #96B7RareGathering2Cooling5Transporting5](https://palworld.gg/pal/beakon-cryst)
[Leaf elementBeegardeBeegarde #674CommonPlanting2Handiwork2Gathering3Deforesting2Medicine Production2Transporting2Farming3](https://palworld.gg/pal/beegarde)
[Dark elementBellanoirBellanoir #19520LegendaryHandiwork5Medicine Production5Transporting4](https://palworld.gg/pal/bellanoir)
[Dark elementBellanoir LiberoBellanoir Libero #195B20LegendaryHandiwork6Medicine Production7Transporting4](https://palworld.gg/pal/bellanoir-libero)
[Fire elementBlazamutBlazamut #1379EpicKindling6Mining7](https://palworld.gg/pal/blazamut)
[Dragon elementFire elementBlazamut RyuBlazamut Ryu #137B10EpicKindling6Mining7](https://palworld.gg/pal/blazamut-ryu)
[Fire elementBlazehowlBlazehowl #1127RareKindling5Deforesting3](https://palworld.gg/pal/blazehowl)
[Fire elementDark elementBlazehowl NoctBlazehowl Noct #112B8EpicKindling5Deforesting3](https://palworld.gg/pal/blazehowl-noct)
[Water elementBlue SlimeBlue Slime 3CommonTransporting1](https://palworld.gg/pal/blue-slime)
[Leaf elementEarth elementBralohaBraloha #1108EpicPlanting5Gathering5Mining3](https://palworld.gg/pal/braloha)
[Leaf elementBristlaBristla #601CommonPlanting2Handiwork2Gathering2Medicine Production2Transporting1](https://palworld.gg/pal/bristla)
[Leaf elementBroncherryBroncherry #1088EpicPlanting5](https://palworld.gg/pal/broncherry)
[Leaf elementWater elementBroncherry AquaBroncherry Aqua #108B8EpicWatering5](https://palworld.gg/pal/broncherry-aqua)
[Earth elementNEWBulldosuBulldosu #1564CommonMining4Transporting3](https://palworld.gg/pal/bulldosu)
[Fire elementBushiBushi #857RareKindling2Handiwork2Gathering1Deforesting3Transporting2](https://palworld.gg/pal/bushi)
[Fire elementDark elementBushi NoctBushi Noct #85B7RareKindling2Handiwork2Gathering1Deforesting5Transporting2](https://palworld.gg/pal/bushi-noct)
[Leaf elementCaprityCaprity #343CommonPlanting2Farming1](https://palworld.gg/pal/caprity)
[Dark elementCaprity NoctCaprity Noct #34B3CommonPlanting2Farming1](https://palworld.gg/pal/caprity-noct)
[Leaf elementNEWCarniboraCarnibora #1366RarePlanting6Handiwork4Gathering4Transporting2](https://palworld.gg/pal/carnibora)
[Normal elementCattivaCattiva #21CommonHandiwork1Gathering1Mining1Transporting1](https://palworld.gg/pal/cattiva)
[Normal elementCave BatCave Bat 3CommonGathering1](https://palworld.gg/pal/cave-bat)
[Dark elementCawgnitoCawgnito #573CommonDeforesting2Farming1](https://palworld.gg/pal/cawgnito)
[Water elementCelarayCelaray #73CommonWatering1Transporting1](https://palworld.gg/pal/celaray)
[Water elementElectricity elementCelaray LuxCelaray Lux #7B4CommonWatering1Generating Electricity2Transporting1](https://palworld.gg/pal/celaray-lux)
[Normal elementCelesdirCelesdir #1576RareGathering4Deforesting7](https://palworld.gg/pal/celesdir)
[Dark elementNEWCelesdir NoctCelesdir Noct #157B7RareGathering4Deforesting8](https://palworld.gg/pal/celesdir-noct)
[Normal elementChikipiChikipi #31CommonGathering1Farming1](https://palworld.gg/pal/chikipi)
[Ice elementDragon elementChilletChillet #1034CommonGathering1Cooling2](https://palworld.gg/pal/chillet)
[Fire elementDragon elementChillet IgnisChillet Ignis #103B5RareKindling4Gathering3](https://palworld.gg/pal/chillet-ignis)
[Leaf elementCinnamothCinnamoth #614CommonPlanting2Gathering2Medicine Production2](https://palworld.gg/pal/cinnamoth)
[Leaf elementNormal elementNEWCloveeClovee #142CommonPlanting1Gathering1](https://palworld.gg/pal/clovee)
[Normal elementCremisCremis #81CommonGathering1Farming2](https://palworld.gg/pal/cremis)
[Water elementCroajiroCroajiro #94CommonWatering1Handiwork1Gathering1Transporting1](https://palworld.gg/pal/croajiro)
[Water elementDark elementCroajiro NoctCroajiro Noct #9B5RareWatering1Handiwork2Gathering1Transporting1](https://palworld.gg/pal/croajiro-noct)
[Ice elementCryolinxCryolinx #1327RareHandiwork3Deforesting4Cooling4Transporting4](https://palworld.gg/pal/cryolinx)
[Earth elementCryolinx TerraCryolinx Terra #132B7RareHandiwork2Deforesting6Mining5Transporting4](https://palworld.gg/pal/cryolinx-terra)
[Dark elementDaedreamDaedream #221CommonHandiwork1Gathering1Transporting1](https://palworld.gg/pal/daedream)
[Leaf elementDark elementNEWDandilordDandilord #1948EpicPlanting8Handiwork6Gathering5Medicine Production6Transporting3](https://palworld.gg/pal/dandilord)
[Earth elementDazemuDazemu #1235RareGathering2](https://palworld.gg/pal/dazemu)
[Electricity elementDazziDazzi #922CommonGenerating Electricity3Handiwork2Transporting2](https://palworld.gg/pal/dazzi)
[Dark elementElectricity elementDazzi NoctDazzi Noct #92B2CommonGenerating Electricity1Handiwork1Medicine Production1Transporting2](https://palworld.gg/pal/dazzi-noct)
[Dark elementDemon EyeDemon Eye 3CommonTransporting1](https://palworld.gg/pal/demon-eye)
[Dark elementDepressoDepresso #161CommonHandiwork1Mining1Transporting1Farming1](https://palworld.gg/pal/depresso)
[Earth elementDigtoiseDigtoise #1075RareMining4](https://palworld.gg/pal/digtoise)
[Leaf elementDragon elementDinossomDinossom #846RarePlanting3Deforesting3](https://palworld.gg/pal/dinossom)
[Electricity elementDragon elementDinossom LuxDinossom Lux #84B7RareGenerating Electricity3Deforesting4](https://palworld.gg/pal/dinossom-lux)
[Normal elementDirehowlDirehowl #332CommonGathering1](https://palworld.gg/pal/direhowl)
[Normal elementDogenDogen #1556RareHandiwork4Gathering3Deforesting3Medicine Production2Transporting3](https://palworld.gg/pal/dogen)
[Earth elementLeaf elementNEWDualithDualith #1388EpicPlanting3Gathering3Deforesting5Mining6Transporting6](https://palworld.gg/pal/dualith)
[Earth elementDark elementNEWDualith NoctDualith Noct #138B8EpicPlanting3Gathering3Deforesting5Mining6Transporting6](https://palworld.gg/pal/dualith-noct)
[Earth elementWater elementDumudDumud #1094CommonWatering2Mining2Transporting1Farming1](https://palworld.gg/pal/dumud)
[Earth elementWater elementDumud GildDumud Gild #109B5RareWatering2Mining2Transporting1Farming4](https://palworld.gg/pal/dumud-gild)
[Fire elementNEWDupinDupin #1767RareKindling7Handiwork5Medicine Production4Transporting2](https://palworld.gg/pal/dupin)
[Electricity elementNEWDynamoffDynamoff #1726RareGenerating Electricity6Gathering3Transporting3](https://palworld.gg/pal/dynamoff)
[Dragon elementDark elementNEWEidrolonEidrolon #1717RareTransporting6](https://palworld.gg/pal/eidrolon)
[Dragon elementFire elementNEWEidrolon IgnisEidrolon Ignis #171B8EpicKindling6Transporting6](https://palworld.gg/pal/eidrolon-ignis)
[Normal elementEikthyrdeerEikthyrdeer #325RareDeforesting2](https://palworld.gg/pal/eikthyrdeer)
[Earth elementEikthyrdeer TerraEikthyrdeer Terra #32B6RareDeforesting2](https://palworld.gg/pal/eikthyrdeer-terra)
[Leaf elementNEWElgroveElgrove #816RarePlanting3Gathering2Deforesting3Mining2Transporting3](https://palworld.gg/pal/elgrove)
[Ice elementNEWElgrove CrystElgrove Cryst #81B7RareDeforesting3Mining3Cooling5Transporting3](https://palworld.gg/pal/elgrove-cryst)
[Leaf elementElizabeeElizabee #688EpicPlanting4Handiwork4Gathering4Deforesting3Medicine Production4](https://palworld.gg/pal/elizabee)
[Dragon elementElphidranElphidran #637RareDeforesting3](https://palworld.gg/pal/elphidran)
[Dragon elementWater elementElphidran AquaElphidran Aqua #63B8EpicWatering4Deforesting3](https://palworld.gg/pal/elphidran-aqua)
[Normal elementEnchanted SwordEnchanted Sword 3CommonDeforesting1](https://palworld.gg/pal/enchanted-sword)
[Dark elementEye of CthulhuEye of Cthulhu 6RareTransporting4](https://palworld.gg/pal/eye-of-cthulhu)
[Fire elementFalerisFaleris #1889EpicKindling6Transporting3](https://palworld.gg/pal/faleris)
[Water elementFaleris AquaFaleris Aqua #188B9EpicWatering6Transporting5](https://palworld.gg/pal/faleris-aqua)
[Dark elementFelbatFelbat #656RareMedicine Production3](https://palworld.gg/pal/felbat)
[Normal elementFenglopeFenglope #833CommonDeforesting3](https://palworld.gg/pal/fenglope)
[Electricity elementFenglope LuxFenglope Lux #83B3CommonGenerating Electricity5Deforesting4](https://palworld.gg/pal/fenglope-lux)
[Water elementFinsiderFinsider #883CommonWatering2Transporting1](https://palworld.gg/pal/finsider)
[Water elementFire elementFinsider IgnisFinsider Ignis #88B4CommonKindling2Watering2Transporting1](https://palworld.gg/pal/finsider-ignis)
[Fire elementFlambelleFlambelle #251CommonKindling1Handiwork1Transporting1Farming1](https://palworld.gg/pal/flambelle)
[Fire elementNEWFlaracleFlaracle #1747RareKindling7Handiwork6Transporting2](https://palworld.gg/pal/flaracle)
[Leaf elementFlopieFlopie #771CommonPlanting2Handiwork2Gathering2Medicine Production1Transporting1](https://palworld.gg/pal/flopie)
[Ice elementFoxcicleFoxcicle #955RareCooling4Farming3](https://palworld.gg/pal/foxcicle)
[Fire elementFoxparksFoxparks #291CommonKindling1](https://palworld.gg/pal/foxparks)
[Ice elementFoxparks CrystFoxparks Cryst #29B1CommonCooling2](https://palworld.gg/pal/foxparks-cryst)
[Ice elementFrostallionFrostallion #20020LegendaryCooling7](https://palworld.gg/pal/frostallion)
[Dark elementFrostallion NoctFrostallion Noct #200B20LegendaryGathering7](https://palworld.gg/pal/frostallion-noct)
[Ice elementFrostplumeFrostplume #1144CommonGathering2Cooling4](https://palworld.gg/pal/frostplume)
[Water elementFuackFuack #51CommonWatering1Handiwork1Transporting1](https://palworld.gg/pal/fuack)
[Water elementFire elementFuack IgnisFuack Ignis #5B2CommonKindling2Watering2Handiwork1Transporting1](https://palworld.gg/pal/fuack-ignis)
[Earth elementFuddlerFuddler #311CommonHandiwork1Mining1Transporting1](https://palworld.gg/pal/fuddler)
[Normal elementGaleclawGaleclaw #492CommonGathering2](https://palworld.gg/pal/galeclaw)
[Dark elementWater elementGhanglerGhangler #975RareWatering5Transporting2](https://palworld.gg/pal/ghangler)
[Fire elementWater elementGhangler IgnisGhangler Ignis #97B6RareKindling5Watering5Transporting2](https://palworld.gg/pal/ghangler-ignis)
[Earth elementGildaneGildane #1548EpicGathering5](https://palworld.gg/pal/gildane)
[Dark elementEarth elementNEWGildraGildra #1205RareHandiwork5Medicine Production4Transporting2](https://palworld.gg/pal/gildra)
[Water elementDark elementGloopieGloopie #485RareWatering2Handiwork2Transporting2](https://palworld.gg/pal/gloopie)
[Water elementNormal elementNEWGloopie PrimoGloopie Primo #48B6RareWatering2Handiwork2Transporting2](https://palworld.gg/pal/gloopie-primo)
[Water elementGobfinGobfin #552CommonWatering2Handiwork2Transporting1](https://palworld.gg/pal/gobfin)
[Fire elementGobfin IgnisGobfin Ignis #55B3CommonKindling2Handiwork2Transporting1](https://palworld.gg/pal/gobfin-ignis)
[Normal elementGoriratGorirat #745RareHandiwork2Deforesting3Transporting3](https://palworld.gg/pal/gorirat)
[Earth elementGorirat TerraGorirat Terra #74B5RareHandiwork2Mining3Transporting3](https://palworld.gg/pal/gorirat-terra)
[Leaf elementGreen SlimeGreen Slime 3CommonTransporting1](https://palworld.gg/pal/green-slime)
[Normal elementGrintaleGrintale #706RareGathering3](https://palworld.gg/pal/grintale)
[Electricity elementGrizzboltGrizzbolt #1858EpicGenerating Electricity5Handiwork4Deforesting3Transporting5](https://palworld.gg/pal/grizzbolt)
[Leaf elementEarth elementGumossGumoss #121CommonPlanting1](https://palworld.gg/pal/gumoss)
[Earth elementHangyuHangyu #381CommonHandiwork1Gathering1Transporting2](https://palworld.gg/pal/hangyu)
[Ice elementHangyu CrystHangyu Cryst #38B2CommonHandiwork3Gathering2Cooling2Transporting3](https://palworld.gg/pal/hangyu-cryst)
[Normal elementNEWHartalisHartalis #19710EpicGathering7Deforesting7](https://palworld.gg/pal/hartalis)
[Dark elementHelzephyrHelzephyr #807RareTransporting4](https://palworld.gg/pal/helzephyr)
[Dark elementElectricity elementHelzephyr LuxHelzephyr Lux #80B8EpicGenerating Electricity4Transporting5](https://palworld.gg/pal/helzephyr-lux)
[Leaf elementNormal elementHerbilHerbil #103CommonPlanting1Gathering1Transporting1](https://palworld.gg/pal/herbil)
[Dark elementHoocratesHoocrates #191CommonGathering1](https://palworld.gg/pal/hoocrates)
[Dark elementNEWHoodleHoodle #1663CommonHandiwork1Transporting1](https://palworld.gg/pal/hoodle)
[Ice elementIcelynIcelyn #1194CommonHandiwork5Medicine Production4Cooling5Transporting2](https://palworld.gg/pal/icelyn)
[Normal elementIlluminant BatIlluminant Bat 4CommonGathering1](https://palworld.gg/pal/illuminant-bat)
[Normal elementIlluminant SlimeIlluminant Slime 4CommonTransporting1](https://palworld.gg/pal/illuminant-slime)
[Fire elementDark elementIncineramIncineram #914CommonKindling3Handiwork2Mining3Transporting2](https://palworld.gg/pal/incineram)
[Dark elementIncineram NoctIncineram Noct #91B5RareHandiwork3Mining4Transporting3](https://palworld.gg/pal/incineram-noct)
[Water elementJellietteJelliette #453CommonWatering2Handiwork1Transporting1](https://palworld.gg/pal/jelliette)
[Water elementDark elementJellroyJellroy #463CommonWatering2Handiwork1Medicine Production1Transporting1](https://palworld.gg/pal/jellroy)
[Dragon elementJetragonJetragon #20220LegendaryGathering8](https://palworld.gg/pal/jetragon)
[Electricity elementJolthogJolthog #151CommonGenerating Electricity1](https://palworld.gg/pal/jolthog)
[Ice elementJolthog CrystJolthog Cryst #15B2CommonCooling1](https://palworld.gg/pal/jolthog-cryst)
[Dragon elementWater elementJormuntideJormuntide #1218EpicWatering7](https://palworld.gg/pal/jormuntide)
[Dragon elementFire elementJormuntide IgnisJormuntide Ignis #121B9EpicKindling7](https://palworld.gg/pal/jormuntide-ignis)
[Dark elementKatressKatress #796RareHandiwork3Medicine Production3Transporting2](https://palworld.gg/pal/katress)
[Dark elementFire elementKatress IgnisKatress Ignis #79B6RareKindling3Handiwork3Medicine Production3Transporting2](https://palworld.gg/pal/katress-ignis)
[Water elementKelpseaKelpsea #431CommonWatering1Farming1](https://palworld.gg/pal/kelpsea)
[Fire elementKelpsea IgnisKelpsea Ignis #43B2CommonKindling1Farming1](https://palworld.gg/pal/kelpsea-ignis)
[Earth elementKikitKikit #1264CommonMining1](https://palworld.gg/pal/kikit)
[Dark elementWater elementKillamariKillamari #301CommonWatering1Gathering1Transporting2](https://palworld.gg/pal/killamari)
[Normal elementWater elementKillamari PrimoKillamari Primo #30B2CommonWatering1Gathering1Transporting2](https://palworld.gg/pal/killamari-primo)
[Normal elementKingpacaKingpaca #218EpicGathering2](https://palworld.gg/pal/kingpaca)
[Ice elementKingpaca CrystKingpaca Cryst #21B9EpicGathering2Cooling4](https://palworld.gg/pal/kingpaca-cryst)
[Fire elementKitsunKitsun #1116RareKindling3](https://palworld.gg/pal/kitsun)
[Dark elementKitsun NoctKitsun Noct #111B6RareKindling4](https://palworld.gg/pal/kitsun-noct)
[Earth elementKnocklemKnocklem #1599EpicGathering4Mining7Transporting7](https://palworld.gg/pal/knocklem)
[Fire elementNEWKnocklem IgnisKnocklem Ignis #159B10EpicKindling5Mining7Transporting7](https://palworld.gg/pal/knocklem-ignis)
[Normal elementLamballLamball #11CommonHandiwork1Transporting1Farming1](https://palworld.gg/pal/lamball)
[Earth elementNEWLapironLapiron #1653CommonHandiwork3Gathering4Mining2Transporting1](https://palworld.gg/pal/lapiron)
[Normal elementNEWLapureLapure #1704CommonHandiwork6Gathering5](https://palworld.gg/pal/lapure)
[Leaf elementNEWLeafanLeafan #907RarePlanting3Handiwork3Gathering3Transporting2](https://palworld.gg/pal/leafan)
[Dark elementLeezpunkLeezpunk #732CommonHandiwork2Gathering1Transporting1](https://palworld.gg/pal/leezpunk)
[Fire elementLeezpunk IgnisLeezpunk Ignis #73B3CommonKindling2Handiwork2Gathering1Transporting1](https://palworld.gg/pal/leezpunk-ignis)
[Leaf elementLifmunkLifmunk #41CommonPlanting1Handiwork1Gathering1Deforesting1Medicine Production1](https://palworld.gg/pal/lifmunk)
[Dark elementFire elementNEWLoomenLoomen #1805RareKindling4Handiwork4Medicine Production4](https://palworld.gg/pal/loomen)
[Dark elementLoupmoonLoupmoon #563CommonHandiwork2](https://palworld.gg/pal/loupmoon)
[Ice elementLoupmoon CrystLoupmoon Cryst #56B3CommonHandiwork4Cooling4](https://palworld.gg/pal/loupmoon-cryst)
[Dark elementLovanderLovander #695RareHandiwork3Mining2Medicine Production3Transporting2](https://palworld.gg/pal/lovander)
[Leaf elementLulluLullu #1254CommonPlanting3Handiwork3Gathering2Medicine Production3](https://palworld.gg/pal/lullu)
[Normal elementLunarisLunaris #826RareHandiwork4Gathering2Transporting2](https://palworld.gg/pal/lunaris)
[Leaf elementLyleenLyleen #1869EpicPlanting7Handiwork5Gathering6Medicine Production5](https://palworld.gg/pal/lyleen)
[Dark elementLyleen NoctLyleen Noct #186B10EpicHandiwork5Gathering6Medicine Production7](https://palworld.gg/pal/lyleen-noct)
[Dark elementFire elementNEWMajexMajex #1155RareKindling4Handiwork5Medicine Production3Transporting2](https://palworld.gg/pal/majex)
[Leaf elementEarth elementMammorestMammorest #878EpicPlanting4Deforesting4Mining4](https://palworld.gg/pal/mammorest)
[Ice elementEarth elementMammorest CrystMammorest Cryst #87B9EpicDeforesting5Mining4Cooling5](https://palworld.gg/pal/mammorest-cryst)
[Dark elementMaraithMaraith #1176RareGathering4Mining4](https://palworld.gg/pal/maraith)
[Dark elementMauMau #271CommonGathering1Farming1](https://palworld.gg/pal/mau)
[Ice elementMau CrystMau Cryst #27B2CommonCooling1Farming1](https://palworld.gg/pal/mau-cryst)
[Normal elementMelpacaMelpaca #203CommonFarming2](https://palworld.gg/pal/melpaca)
[Dark elementEarth elementMenastingMenasting #999EpicDeforesting3Mining5](https://palworld.gg/pal/menasting)
[Earth elementMenasting TerraMenasting Terra #99B10EpicDeforesting3Mining6](https://palworld.gg/pal/menasting-terra)
[Normal elementMimogMimog #1447RareGathering1Transporting2](https://palworld.gg/pal/mimog)
[Fire elementEarth elementNEWMoldronMoldron #1057RareKindling5Mining5](https://palworld.gg/pal/moldron)
[Ice elementEarth elementNEWMoldron CrystMoldron Cryst #105B8EpicMining5Cooling5](https://palworld.gg/pal/moldron-cryst)
[Leaf elementMossandaMossanda #1026RarePlanting3Handiwork2Deforesting4Transporting4](https://palworld.gg/pal/mossanda)
[Electricity elementMossanda LuxMossanda Lux #102B7RareGenerating Electricity4Handiwork3Deforesting4Transporting4](https://palworld.gg/pal/mossanda-lux)
[Normal elementMozzarinaMozzarina #402CommonFarming2](https://palworld.gg/pal/mozzarina)
[Ice elementNEWMufflyMuffly #592CommonCooling2Transporting1](https://palworld.gg/pal/muffly)
[Ice elementWater elementMunchillMunchill #863CommonWatering2Cooling3Transporting1](https://palworld.gg/pal/munchill)
[Leaf elementNEWMycoraMycora #1796RarePlanting6Handiwork4Gathering4Medicine Production6](https://palworld.gg/pal/mycora)
[Dark elementNecromusNecromus #19920LegendaryDeforesting6Mining6](https://palworld.gg/pal/necromus)
[Leaf elementNEWNeedollNeedoll #1002CommonPlanting3Gathering3Transporting1](https://palworld.gg/pal/needoll)
[Dark elementLeaf elementNEWNeedoll NoctNeedoll Noct #100B3CommonPlanting3Gathering3Transporting1](https://palworld.gg/pal/needoll-noct)
[Water elementNeptiliusNeptilius #20120LegendaryWatering7](https://palworld.gg/pal/neptilius)
[Dark elementNitemaryNitemary #1486RareHandiwork4Transporting2](https://palworld.gg/pal/nitemary)
[Leaf elementNEWNitemary BotanNitemary Botan #148B7RarePlanting3Handiwork4Transporting2](https://palworld.gg/pal/nitemary-botan)
[Normal elementNitewingNitewing #513CommonGathering2](https://palworld.gg/pal/nitewing)
[Dark elementNoxNox #246RareGathering1](https://palworld.gg/pal/nox)
[Dark elementNyafiaNyafia #1434CommonHandiwork4Gathering4Deforesting2Transporting3](https://palworld.gg/pal/nyafia)
[Dark elementOmasculOmascul #1504CommonGathering5](https://palworld.gg/pal/omascul)
[Leaf elementWater elementNEWOphydiaOphydia #1759EpicWatering5Planting7](https://palworld.gg/pal/ophydia)
[Dragon elementElectricity elementOrserkOrserk #1879EpicGenerating Electricity8Handiwork3Transporting4](https://palworld.gg/pal/orserk)
[Normal elementPaladiusPaladius #19820LegendaryDeforesting6Mining6](https://palworld.gg/pal/paladius)
[Leaf elementPalumbaPalumba #1066RarePlanting4Gathering4Mining5](https://palworld.gg/pal/palumba)
[Water elementNEWPanthalusPanthalus #20310Epic](https://palworld.gg/pal/panthalus)
[Water elementIce elementPengulletPengullet #171CommonWatering1Handiwork1Cooling1Transporting1](https://palworld.gg/pal/pengullet)
[Water elementElectricity elementPengullet LuxPengullet Lux #17B2CommonWatering1Generating Electricity2Handiwork1Transporting1](https://palworld.gg/pal/pengullet-lux)
[Water elementIce elementPenkingPenking #186RareWatering2Handiwork2Mining3Cooling2Transporting3](https://palworld.gg/pal/penking)
[Water elementElectricity elementPenking LuxPenking Lux #18B7RareWatering2Generating Electricity3Handiwork2Mining3Transporting3](https://palworld.gg/pal/penking-lux)
[Leaf elementPetalliaPetallia #898EpicPlanting4Handiwork3Gathering3Medicine Production4Transporting2](https://palworld.gg/pal/petallia)
[Leaf elementFire elementNEWPetallia IgnisPetallia Ignis #89B9EpicKindling4Handiwork3Gathering3Medicine Production4Transporting2](https://palworld.gg/pal/petallia-ignis)
[Earth elementNEWPierdonPierdon #1316RareMining5](https://palworld.gg/pal/pierdon)
[Ice elementNEWPierdon CrystPierdon Cryst #131B7RareMining5Cooling6](https://palworld.gg/pal/pierdon-cryst)
[Ice elementWater elementPolapupPolapup #725RareWatering3Cooling4](https://palworld.gg/pal/polapup)
[Ice elementEarth elementNEWPolapup TerraPolapup Terra #72B6RareMining4Cooling4](https://palworld.gg/pal/polapup-terra)
[Dark elementEarth elementPrixterPrixter #1415RareGathering2Deforesting4Medicine Production2](https://palworld.gg/pal/prixter)
[Electricity elementEarth elementNEWPrixter LuxPrixter Lux #141B6RareGenerating Electricity3Gathering2Deforesting4Medicine Production2](https://palworld.gg/pal/prixter-lux)
[Leaf elementDark elementPruneliaPrunelia #1475RarePlanting3Handiwork1Gathering2Medicine Production3Transporting1](https://palworld.gg/pal/prunelia)
[Electricity elementNEWPuffoltPuffolt #622CommonGenerating Electricity2Transporting1](https://palworld.gg/pal/puffolt)
[Earth elementNEWPupperaiPupperai #132CommonGathering1Deforesting1Transporting1](https://palworld.gg/pal/pupperai)
[Dark elementPurple SlimePurple Slime 3CommonTransporting1](https://palworld.gg/pal/purple-slime)
[Fire elementPyrinPyrin #936RareKindling4Deforesting2](https://palworld.gg/pal/pyrin)
[Fire elementDark elementPyrin NoctPyrin Noct #93B7RareKindling4Deforesting3](https://palworld.gg/pal/pyrin-noct)
[Dragon elementQuivernQuivern #1247RareHandiwork2Gathering3Mining4Transporting5](https://palworld.gg/pal/quivern)
[Dragon elementLeaf elementQuivern BotanQuivern Botan #124B8EpicPlanting5Handiwork2Gathering4Mining3Transporting4](https://palworld.gg/pal/quivern-botan)
[Fire elementRagnahawkRagnahawk #1047RareKindling4Transporting5](https://palworld.gg/pal/ragnahawk)
[Normal elementRainbow SlimeRainbow Slime 4CommonTransporting1](https://palworld.gg/pal/rainbow-slime)
[Electricity elementRayhoundRayhound #985RareGenerating Electricity4](https://palworld.gg/pal/rayhound)
[Ice elementNEWRayhound CrystRayhound Cryst #98B6RareCooling3](https://palworld.gg/pal/rayhound-cryst)
[Fire elementRed SlimeRed Slime 3CommonTransporting1](https://palworld.gg/pal/red-slime)
[Ice elementReindrixReindrix #1014CommonDeforesting3Cooling3](https://palworld.gg/pal/reindrix)
[Dragon elementWater elementRelaxaurusRelaxaurus #948EpicWatering3Transporting3](https://palworld.gg/pal/relaxaurus)
[Dragon elementElectricity elementRelaxaurus LuxRelaxaurus Lux #94B9EpicGenerating Electricity4Transporting3](https://palworld.gg/pal/relaxaurus-lux)
[Fire elementNEWRenjishiRenjishi #1837RareKindling8Handiwork6Gathering5Transporting5](https://palworld.gg/pal/renjishi)
[Fire elementEarth elementReptyroReptyro #1296RareKindling5Mining5](https://palworld.gg/pal/reptyro)
[Ice elementEarth elementReptyro CrystReptyro Cryst #129B7RareMining5Cooling5](https://palworld.gg/pal/reptyro-cryst)
[Normal elementRibbunyRibbuny #441CommonHandiwork1Gathering1Transporting1](https://palworld.gg/pal/ribbuny)
[Leaf elementRibbuny BotanRibbuny Botan #44B1CommonPlanting2Handiwork2Gathering2Transporting1](https://palworld.gg/pal/ribbuny-botan)
[Leaf elementRobinquillRobinquill #765RarePlanting2Handiwork3Gathering3Deforesting2Medicine Production1Transporting2](https://palworld.gg/pal/robinquill)
[Leaf elementEarth elementRobinquill TerraRobinquill Terra #76B6RareHandiwork3Gathering3Deforesting2Medicine Production2Transporting2](https://palworld.gg/pal/robinquill-terra)
[Fire elementRoobyRooby #262CommonKindling1Farming1](https://palworld.gg/pal/rooby)
[Dark elementNEWRoujayRoujay #1775RareGathering5Transporting5](https://palworld.gg/pal/roujay)
[Earth elementRushoarRushoar #281CommonMining1](https://palworld.gg/pal/rushoar)
[Earth elementNEWSekhmetSekhmet #1405RareHandiwork6Mining3Transporting2](https://palworld.gg/pal/sekhmet)
[Dark elementNormal elementSelyneSelyne #1909EpicHandiwork7Medicine Production6Transporting3](https://palworld.gg/pal/selyne)
[Dark elementShadowbeakShadowbeak #18910EpicGathering2](https://palworld.gg/pal/shadowbeak)
[Dragon elementWater elementNEWShaolongShaolong #1929EpicWatering8Gathering5](https://palworld.gg/pal/shaolong)
[Leaf elementShroomerShroomer #1184CommonPlanting3Handiwork2Gathering3Deforesting2Farming3](https://palworld.gg/pal/shroomer)
[Leaf elementDark elementShroomer NoctShroomer Noct #118B5RarePlanting3Handiwork3Gathering3Deforesting2](https://palworld.gg/pal/shroomer-noct)
[Ice elementSibelyxSibelyx #1167RareMedicine Production3Cooling3Farming3](https://palworld.gg/pal/sibelyx)
[Normal elementNEWSibelyx PrimoSibelyx Primo #116B8EpicMedicine Production3Farming4](https://palworld.gg/pal/sibelyx-primo)
[Leaf elementNEWSilvanceSilvance #1938EpicPlanting6Handiwork6Gathering4Medicine Production8Transporting2](https://palworld.gg/pal/silvance)
[Dragon elementSilvegisSilvegis #1608EpicDeforesting6](https://palworld.gg/pal/silvegis)
[Water elementNEWSkutlassSkutlass #1285RareWatering4Gathering1Deforesting4](https://palworld.gg/pal/skutlass)
[Water elementFire elementNEWSkutlass IgnisSkutlass Ignis #128B5RareKindling3Watering2Gathering2Deforesting3](https://palworld.gg/pal/skutlass-ignis)
[Electricity elementNEWSlowattSlowatt #1674CommonGenerating Electricity3](https://palworld.gg/pal/slowatt)
[Dark elementSmokieSmokie #1492CommonGathering2](https://palworld.gg/pal/smokie)
[Dark elementIce elementNEWSmokie CrystSmokie Cryst #149B3CommonGathering2Cooling2](https://palworld.gg/pal/smokie-cryst)
[Electricity elementNEWSnockSnock #1632CommonGenerating Electricity4](https://palworld.gg/pal/snock)
[Electricity elementEarth elementNEWSnock LuxSnock Lux #163B3CommonGenerating Electricity4](https://palworld.gg/pal/snock-lux)
[Ice elementNEWSnuglooSnugloo #1333CommonHandiwork2Mining3Cooling3Transporting2](https://palworld.gg/pal/snugloo)
[Dark elementNormal elementNEWSolenneSolenne #1827RareHandiwork8Gathering4Transporting2](https://palworld.gg/pal/solenne)
[Water elementNEWSolmoraSolmora #1694CommonWatering4](https://palworld.gg/pal/solmora)
[Water elementElectricity elementNEWSolmora LuxSolmora Lux #169B5RareWatering4Generating Electricity6](https://palworld.gg/pal/solmora-lux)
[Dark elementFire elementSootseerSootseer #1357RareKindling3Handiwork3Gathering2Mining3Farming2](https://palworld.gg/pal/sootseer)
[Leaf elementNEWSoufflineSouffline #1643CommonPlanting2Transporting2](https://palworld.gg/pal/souffline)
[Electricity elementSparkitSparkit #421CommonGenerating Electricity1Handiwork1Transporting1Farming1](https://palworld.gg/pal/sparkit)
[Dark elementSplatterinaSplatterina #1534CommonHandiwork6Deforesting3Medicine Production5Transporting2](https://palworld.gg/pal/splatterina)
[Dark elementStarryonStarryon #1307RareGathering5](https://palworld.gg/pal/starryon)
[Normal elementNEWStarryon PrimoStarryon Primo #130B8EpicGathering7](https://palworld.gg/pal/starryon-primo)
[Water elementSurfentSurfent #754CommonWatering3Farming2](https://palworld.gg/pal/surfent)
[Earth elementSurfent TerraSurfent Terra #75B5RareGathering3](https://palworld.gg/pal/surfent-terra)
[Fire elementSuzakuSuzaku #1228EpicKindling5](https://palworld.gg/pal/suzaku)
[Water elementSuzaku AquaSuzaku Aqua #122B9EpicWatering6](https://palworld.gg/pal/suzaku-aqua)
[Ice elementSweeSwee #351CommonGathering1Cooling1](https://palworld.gg/pal/swee)
[Ice elementSweepaSweepa #366RareGathering2Cooling3](https://palworld.gg/pal/sweepa)
[Leaf elementTanzeeTanzee #231CommonPlanting1Handiwork1Gathering1Deforesting1Transporting1](https://palworld.gg/pal/tanzee)
[Fire elementNEWTanzee IgnisTanzee Ignis #23B2CommonKindling1Handiwork1Deforesting1Transporting1](https://palworld.gg/pal/tanzee-ignis)
[Dark elementTarantrissTarantriss #713CommonHandiwork3Gathering3Medicine Production2Transporting2](https://palworld.gg/pal/tarantriss)
[Water elementTeafantTeafant #111CommonWatering1](https://palworld.gg/pal/teafant)
[Earth elementNEWTetroise Tetroise #1428EpicMining4](https://palworld.gg/pal/tetroise)
[Normal elementNEWTetroise PrimoTetroise Primo #142B8EpicMining6](https://palworld.gg/pal/tetroise-primo)
[Normal elementTocotocoTocotoco #531CommonGathering1](https://palworld.gg/pal/tocotoco)
[Dark elementTombatTombat #525RareGathering2Mining3Transporting2](https://palworld.gg/pal/tombat)
[Leaf elementNEWTropicawTropicaw #1735RarePlanting5Gathering5](https://palworld.gg/pal/tropicaw)
[Water elementTurtacleTurtacle #373CommonWatering2Mining1Transporting1](https://palworld.gg/pal/turtacle)
[Water elementEarth elementTurtacle TerraTurtacle Terra #37B4CommonWatering2Mining3Transporting1](https://palworld.gg/pal/turtacle-terra)
[Electricity elementUnivoltUnivolt #545RareGenerating Electricity3Deforesting1](https://palworld.gg/pal/univolt)
[Ice elementNEWUnivolt CrystUnivolt Cryst #54B6RareDeforesting3Cooling6](https://palworld.gg/pal/univolt-cryst)
[Leaf elementVaeletVaelet #668EpicPlanting3Handiwork3Gathering3Medicine Production3Transporting2Farming2](https://palworld.gg/pal/vaelet)
[Normal elementNEWValentailValentail #1622CommonGathering2](https://palworld.gg/pal/valentail)
[Fire elementDark elementVanwyrmVanwyrm #645RareKindling2Transporting3](https://palworld.gg/pal/vanwyrm)
[Ice elementDark elementVanwyrm CrystVanwyrm Cryst #64B5RareCooling2Transporting3](https://palworld.gg/pal/vanwyrm-cryst)
[Dark elementNEWVenusaVenusa #1785RareHandiwork6Gathering6Medicine Production5Transporting2](https://palworld.gg/pal/venusa)
[Leaf elementVerdashVerdash #1528EpicPlanting4Handiwork5Gathering5Deforesting3Transporting3](https://palworld.gg/pal/verdash)
[Normal elementVixyVixy #62CommonGathering1Farming1](https://palworld.gg/pal/vixy)
[Earth elementLeaf elementWarsectWarsect #1138EpicPlanting3Handiwork3Deforesting4Transporting5](https://palworld.gg/pal/warsect)
[Earth elementWarsect TerraWarsect Terra #113B9EpicHandiwork2Mining5Transporting5](https://palworld.gg/pal/warsect-terra)
[Ice elementWater elementWhalaskaWhalaska #1518EpicWatering5Cooling6](https://palworld.gg/pal/whalaska)
[Ice elementFire elementWhalaska IgnisWhalaska Ignis #151B8EpicKindling5Cooling6](https://palworld.gg/pal/whalaska-ignis)
[Dark elementNEWWispawWispaw #505RareHandiwork2Deforesting1Medicine Production1Transporting1](https://palworld.gg/pal/wispaw)
[Dark elementNEWWistellaWistella #1812CommonHandiwork6Medicine Production6Transporting1](https://palworld.gg/pal/wistella)
[Fire elementWixenWixen #786RareKindling3Handiwork3Transporting2](https://palworld.gg/pal/wixen)
[Fire elementDark elementWixen NoctWixen Noct #78B6RareKindling4Handiwork4Transporting2](https://palworld.gg/pal/wixen-noct)
[Normal elementWoolipopWoolipop #393CommonFarming1](https://palworld.gg/pal/woolipop)
[Earth elementNEWWoolipop TerraWoolipop Terra #39B4CommonFarming1](https://palworld.gg/pal/woolipop-terra)
[Ice elementWumpoWumpo #1347RareHandiwork3Deforesting5Cooling5Transporting6](https://palworld.gg/pal/wumpo)
[Leaf elementWumpo BotanWumpo Botan #134B8EpicPlanting3Handiwork3Deforesting5Transporting6](https://palworld.gg/pal/wumpo-botan)
[Dragon elementXenogardXenogard #1469EpicMining4](https://palworld.gg/pal/xenogard)
[Dark elementDragon elementXenolordXenolord #1968EpicGathering2](https://palworld.gg/pal/xenolord)
[Dark elementXenovaderXenovader #1457RareDeforesting3Transporting2](https://palworld.gg/pal/xenovader)
[Normal elementYakumoYakumo #1274CommonGathering2](https://palworld.gg/pal/yakumo)
"""

ELEMENT_MAP = {
    "Normal": "Neutral", "Fire": "Fire", "Water": "Water",
    "Electricity": "Electric", "Leaf": "Grass", "Dark": "Dark",
    "Dragon": "Dragon", "Earth": "Ground", "Ice": "Ice",
}
ELEM_NAMES = ["Normal", "Fire", "Water", "Electricity", "Leaf", "Dark", "Dragon", "Earth", "Ice"]

# work text label -> csv column
WORK_MAP = {
    "Kindling": "Kindling", "Watering": "Watering", "Planting": "Planting",
    "Generating Electricity": "Generating_Electricity", "Handiwork": "Handiwork",
    "Gathering": "Gathering", "Deforesting": "Lumbering", "Mining": "Mining",
    "Medicine Production": "Medicine", "Cooling": "Cooling",
    "Transporting": "Transporting", "Farming": "Farming",
    "Oil Extracting": "Oil_Extracting",
}
# longest-first ordering so multiword labels match before substrings
WORK_LABELS = ["Generating Electricity", "Medicine Production", "Oil Extracting",
               "Kindling", "Watering", "Planting", "Handiwork", "Gathering",
               "Deforesting", "Mining", "Cooling", "Transporting", "Farming"]

WORK_COLS = ["Kindling", "Watering", "Planting", "Generating_Electricity",
             "Handiwork", "Gathering", "Lumbering", "Mining", "Medicine",
             "Cooling", "Transporting", "Farming"]

RARITY_NAMES = ("Legendary", "Common", "Rare", "Epic")


def dedupe_name(raw, slug):
    s = raw.strip()
    if s and len(s) % 2 == 0 and s[:len(s) // 2] == s[len(s) // 2:]:
        return s[:len(s) // 2]
    # fallback: build from slug
    return " ".join(w.capitalize() for w in slug.split("-"))


def parse_line(line):
    m = re.match(r"\[(.*)\]\(https://palworld\.gg/pal/([^)]+)\)$", line.strip())
    if not m:
        return None
    inner, slug = m.group(1), m.group(2)

    # 1. strip leading "<Element> element" prefixes
    elements = []
    rest = inner
    while True:
        m2 = re.match(r"(" + "|".join(ELEM_NAMES) + r") element", rest)
        if not m2:
            break
        elements.append(ELEMENT_MAP[m2.group(1)])
        rest = rest[m2.end():]

    # 2. optional NEW tag
    if rest.startswith("NEW"):
        rest = rest[3:]

    # 3. locate rarity name (first occurrence)
    rar_pos, rar_name = None, None
    for rn in ("Common", "Rare", "Epic", "Legendary"):
        p = rest.find(rn)
        if p != -1 and (rar_pos is None or p < rar_pos):
            rar_pos, rar_name = p, rn
    if rar_pos is None:
        return None
    pre = rest[:rar_pos]
    works_str = rest[rar_pos + len(rar_name):]

    # 4. number + rarity value out of pre
    number = ""
    if "#" in pre:
        namepart, numtok = pre.split("#", 1)
        numtok = numtok.strip()
        if "B" in numtok:
            bi = numtok.index("B")
            number = numtok[:bi + 1]
        else:
            if rar_name == "Legendary":
                number = numtok[:-2]
            elif rar_name == "Epic":
                number = numtok[:-2] if numtok.endswith("10") else numtok[:-1]
            else:  # Common / Rare -> single-digit rarity
                number = numtok[:-1]
    else:
        # no paldeck number (slimes, collab, etc.)
        m3 = re.search(r"(\d+)\s*$", pre)
        namepart = pre[:m3.start()] if m3 else pre

    name = dedupe_name(namepart, slug)

    # 5. works
    works = {}
    for lbl in WORK_LABELS:
        for mw in re.finditer(re.escape(lbl) + r"(\d+)", works_str):
            works[WORK_MAP[lbl]] = mw.group(1)

    e1 = elements[0] if len(elements) >= 1 else ""
    e2 = elements[1] if len(elements) >= 2 else ""

    row = {
        "Number": number,
        "Name": name,
        "Element_1": e1,
        "Element_2": e2,
        "PaldbURL": "https://paldb.cc/en/" + name.replace(" ", "_"),
    }
    for c in WORK_COLS:
        row[c] = works.get(c, "")
    return row


def main():
    rows = []
    for line in RAW.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        r = parse_line(line)
        if r:
            rows.append(r)

    header = ["Number", "Name", "Element_1", "Element_2"] + WORK_COLS + ["PaldbURL"]
    outdir = os.path.dirname(os.path.abspath(__file__))
    outpath = os.path.join(outdir, "palworld_pals.csv")
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # validation summary
    print("Total rows:", len(rows))
    empty_names = [r for r in rows if not r["Name"].strip()]
    print("Empty names:", len(empty_names))
    no_number = [r["Name"] for r in rows if not r["Number"].strip()]
    print("Rows without paldeck number ({}): {}".format(len(no_number), ", ".join(no_number)))
    dup = {}
    for r in rows:
        dup[r["Name"]] = dup.get(r["Name"], 0) + 1
    print("Duplicate names:", {k: v for k, v in dup.items() if v > 1})
    print("Wrote:", outpath)
    # spot check
    for target in ("Lifmunk", "Foxparks", "Anubis", "Jetragon", "Fuack Ignis", "Jolthog Cryst"):
        for r in rows:
            if r["Name"] == target:
                print("CHECK", target, "|#", r["Number"], "|", r["Element_1"], r["Element_2"],
                      "| works:", {c: r[c] for c in WORK_COLS if r[c]})
                break


if __name__ == "__main__":
    main()
