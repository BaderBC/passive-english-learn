<script lang="ts">
    import {setUrl, UrlParams} from "./App.svelte";
    import BackArrow from "./lib/BackArrow.svelte";

    export let urlPropertyToModify: UrlParams;
    export let propertToComeBack: UrlParams | null = null;
    export let resources: string[];

    function resetChosenChapter() {
        setUrl(propertToComeBack!, '');
    }

    function capitalize(str: string) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
</script>

{#if (propertToComeBack)}
    <div class="back-arrow">
        <BackArrow onClick={resetChosenChapter}/>
    </div>
{/if}

<div class="resources">
    {#each resources as resource}
        {@const resourceName = capitalize(resource.replace('-', ' '))}
        <button on:click={() => setUrl(urlPropertyToModify, resource)}>{resourceName}</button>
    {/each}
</div>

<style>
    .back-arrow {
        position: absolute;
        top: 10px;
        left: 10px;
    }

    .resources {
        margin-top: 70px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .resources > button {
        font-size: 40px;
        font-weight: bold;
        font-family: sans-serif;
        padding: 20px 50px;
        border: none;
        border-radius: 70px;
        background-color: orange;
        color: aliceblue;
    }

    .resources > button:hover {
        background-color: #ffb21b;
    }

    .resources > button:active {
        background-color: #e69a01;
    }
</style>
