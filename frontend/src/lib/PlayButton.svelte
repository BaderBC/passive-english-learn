<script lang="ts">
    import PlayIcon from "./PlayIcon.svelte";
    import PauseIcon from "./PauseIcon.svelte";
    import LoadingIcon from "./LoadingIcon.svelte";
    import type {Status} from "./player";

    export let onClick = () => {
    };
    export let status: Status;
</script>

<button on:click={onClick}>
    {#if (status === 'PLAYING')}
        <PauseIcon/>
    {:else if (status === 'LOADING')}
        <LoadingIcon/>
    {:else}
        <PlayIcon/>
    {/if}
</button>

<style>
    button {
        padding: 10px;
        background-color: #fcfcfc;
        width: min-content;
        height: min-content;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 100%;
        border: 1px solid #272727;
        appearance: none;
    }
</style>