<script lang="ts">
    import backArrowIcon from '../assets/back-arrow-icon.svg';

    export let onClick: () => void = () => null;
</script>

<button on:click={onClick}>
    <img src={backArrowIcon} alt="Back arrow"/>
</button>

<style>
    button {
        display: inline-block;
        width: 48px;
        height: 48px;
        background: none;
        border: none;
        cursor: pointer;
    }
    
    button:hover {
        opacity: 0.8;
    }
    
    button:active {
        opacity: 0.6;
    }
</style>