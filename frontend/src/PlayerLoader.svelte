<script lang="ts">
    import {currentBook, currentChapter} from "./App.svelte";
    import {Player} from "./lib/player";
    import PlayerComponent from "./Player.svelte";
    import {onMount} from "svelte";

    let player: Player | null = null;
    let error: string | null = null;
    onMount(async () => {
        try {
            player = await Player.create($currentBook!, $currentChapter!);
        } catch (e: any) {
            error = e?.message;
        }
    });
</script>

{#if (error)}
    <h1>ERROR: {error}</h1>
{:else if (player)}
    <PlayerComponent bind:player/>
{:else}
    <h1>Loading...</h1>
{/if}
