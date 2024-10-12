<script lang="ts">
    export let onClick = () => {};
</script>

<button on:click={onClick}><slot/></button>

<style>
    button {
        height: min-content;
        padding: 5px 15px;
        border-radius: 20px;
        appearance: none;
        background-color: #fcfcfc;
        border: 1px solid #bbb;
    }
</style>