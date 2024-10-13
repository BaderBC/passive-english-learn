<script lang="ts">
    import {currentBook, currentChapter, setUrl, UrlParams} from "./App.svelte";
    import bookIcon from './assets/book-icon.png';
    import PlayButton from "./lib/PlayButton.svelte";
    import OvalButton from "./lib/OvalButton.svelte";
    import Slider from "./lib/Slider.svelte";
    import RoundedRect from "./lib/RoundedRect.svelte";
    import {Player, type Status} from "./lib/player";
    import {onDestroy, onMount} from "svelte";
    import BackArrow from "./lib/BackArrow.svelte";

    export let player: Player;
    let volumeSliderValue = 100;
    let mainSliderValue = 0;
    let nowPlayingIdx = 0;
    let enWord = player.contentInfo[nowPlayingIdx].en;
    let plWord = player.contentInfo[nowPlayingIdx].pl;
    let status: Status = 'PAUSED';

    const bookName = $currentBook!.replace('-', ' ');
    const chapterName = $currentChapter!.replace('-', ' ');

    $: mainSliderValue, (async () => {
        await player.setCurrentIndex(Math.round(mainSliderValue));
    })();

    $: volumeSliderValue, (() => {
        player.setVolume(volumeSliderValue / 100);
    })();

    player.onStatusChange(s => status = s);
    player.onCurrentIndexChange((idx) => {
        mainSliderValue = idx;
        nowPlayingIdx = idx
        enWord = player.contentInfo[nowPlayingIdx].en;
        plWord = player.contentInfo[nowPlayingIdx].pl;
    });

    function playStop() {
        if (player.status === 'PAUSED') {
            player.play();
        } else if (player.status === 'PLAYING') {
            player.pause();
        }
    }

    function next() {
        player.next(300);
    }

    function prev() {
        player.prev(300);
    }

    let resetChosenChapter = () => undefined;

    onMount(() => {
        const playerElement = document.getElementById('player')!;

        function matchDeviceWidth() {
            const playerWidth = playerElement.offsetWidth;
            const viewportWidth = window.innerWidth;

            const scaleFactor = Math.min(1, (viewportWidth / playerWidth - 0.03));
            playerElement.style.transform = `scale(${scaleFactor})`;
        }

        function handleKeydown(e: KeyboardEvent) {
            switch (e.key) {
                case 'ArrowRight':
                    next();
                    break;
                case 'ArrowLeft':
                    prev();
                    break;
                case ' ':
                    e.preventDefault();
                    playStop();
                    break;
                default:
                    return;
            }
            e.stopImmediatePropagation();
        }

        matchDeviceWidth();
        window.addEventListener('resize', matchDeviceWidth);
        window.addEventListener('keydown', handleKeydown, true);

        resetChosenChapter = () => {
            player.destroy();
            window.removeEventListener('resize', matchDeviceWidth);
            window.removeEventListener('keydown', handleKeydown, true);
            setUrl(UrlParams.Chapter, '');
        }
    });
</script>

<div class="back-arrow">
    <BackArrow onClick={resetChosenChapter}/>
</div>

<section id="player">
    <h1 class="current-book">{bookName}</h1>
    <h1 class="current-chapter">{chapterName}</h1>
    <img src={bookIcon} alt=""/>
    <section class="control-panel">
        <section class="controls-info">
            <div style="display: flex">
                <div class="lang-title"><span>Polish:</span></div>
                <span>{plWord}</span>
            </div>
            <div style="display: flex">
                <div class="lang-title"><span>English:</span></div>
                <span>{enWord}</span>
            </div>
        </section>
        <section class="controls">
            <OvalButton onClick={prev}>Prev</OvalButton>
            <PlayButton onClick={playStop} {status}/>
            <OvalButton onClick={next}>Next</OvalButton>
            <span>Volume</span>
            <div class="volume-slider">
                <Slider
                        bind:value={volumeSliderValue}
                        min={0}
                        max={100}
                        step={0.01}
                        precision={2}
                        formatter='{v => parseFloat(v).toFixed(1) + "%"}'
                />
            </div>
        </section>
        <section class="now-playing-slider">
            <RoundedRect>{nowPlayingIdx + 1}</RoundedRect>
            <div style="width: 100%">
                <Slider
                        bind:value={mainSliderValue}
                        min={0}
                        max={player.playlistLength-1}
                        step={1}
                        precision={0}
                        formatter='{v => Math.round(v)+1}'
                />
            </div>
            <RoundedRect>{player.playlistLength}</RoundedRect>
        </section>
    </section>
</section>

<style>
    .back-arrow {
        position: absolute;
        top: 10px;
        left: 10px;
    }

    h1 {
        color: #000;
        text-shadow: 1px 1px 1px #222;
    }

    .current-book {
        top: 200px;
        left: 265px;
        transform: skew(5deg, -26deg);
        position: absolute;
    }

    .current-chapter {
        top: 220px;
        left: 260px;
        transform: skew(5deg, -26deg) scale(0.9);
        position: absolute;
    }

    .volume-slider {
        width: 40%;
    }

    img {
        width: 400px;
        aspect-ratio: 1/1;
    }

    .controls-info {
        font-size: 14px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .lang-title {
        width: 80px;
    }

    .lang-title > span {
        font-weight: bolder;
    }

    .control-panel {
        display: flex;
        flex-direction: column;
        gap: 16px;
        background-color: #eee;
        border-radius: 15px;
        padding: 15px;
        width: calc(100% - 30px);
    }

    .controls {
        display: flex;
        gap: 15px;
        justify-content: space-evenly;
        align-items: center;
    }

    .now-playing-slider {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    #player {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-radius: 25px;
        background-color: #ffb21b;
        padding: 10px;
        color: darkslategray;
    }
</style>