<script lang="ts" context="module">
    import bookIcon from './assets/book-icon.png';
    import {writable, type Writable} from "svelte/store";

    export enum UrlParams {
        Book = 'book',
        Chapter = 'chapter',
    }

    export let currentChapter: Writable<string | null> = writable(getUrlParameter(UrlParams.Chapter))
    export let currentBook: Writable<string | null> = writable(getUrlParameter(UrlParams.Book));

    function getUrlParameter(key: UrlParams) {
        const val = new URLSearchParams(window.location.search).get(key);
        return val ? val : null;
    }

    export function setUrl(key: UrlParams, val: string) {
        let currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set(key.toString(), val);
        window.history.replaceState({}, '', currentUrl);

        // refresh all url params:
        currentBook.set(getUrlParameter(UrlParams.Book));
        currentChapter.set(getUrlParameter(UrlParams.Chapter));
    }
</script>

<script lang="ts">
    import ChooseResource from "./ChooseResource.svelte";
    import PlayerLoader from "./PlayerLoader.svelte";

    const resources: any = {
        'focus-2': ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-4', 'chapter-5', 'chapter-6', 'chapter-7', 'chapter-8'],
        'focus-3': ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-4', 'chapter-5', 'chapter-6', 'chapter-7', 'chapter-8'],
        'focus-4': ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-4', 'chapter-5', 'chapter-6', 'chapter-7', 'chapter-8'],
    };
</script>

<svelte:head>
    <link rel="icon" type="imgage/png" href={bookIcon}>
</svelte:head>

<main>
    {#if (!$currentBook)}
        <ChooseResource resources={Object.keys(resources)} urlPropertyToModify={UrlParams.Book}/>
    {:else if (!$currentChapter)}
        <ChooseResource resources={resources[$currentBook]} urlPropertyToModify={UrlParams.Chapter}
                        propertToComeBack={UrlParams.Book}/>
    {:else}
        <PlayerLoader/>
    {/if}
</main>

<style>
    main {
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
</style>