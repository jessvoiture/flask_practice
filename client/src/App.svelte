<script>
  let name = '';
  let submittedName = ''; 
  let result = [];
  let isLoading = false;
  let isSubmitted = false;

  async function handleSubmit() {
    isLoading = true;
    isSubmitted = true;
    let res = await fetch(`/wiki?name=${name}`);
    let wiki_result = await res.json();
    if (res.ok) {
      result = wiki_result;
      submittedName = name;
    }
    isLoading = false;
    name = '';
  }

  function handleInputChange() {
    isSubmitted = false;
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      handleSubmit();
    }
  }

  function extractName(url) {
    const parts = url.split('/');
    const lastPart = parts[parts.length - 1];
    const decoded = decodeURIComponent(lastPart.replace(/_/g, ' '));
    return decoded;
  }
</script>

<style>
  ul {
    list-style-type: none;
    padding: 0;
  }
</style>

<input bind:value={name} placeholder="Enter a name" on:input={handleInputChange} on:keydown={handleKeyDown}>
<button on:click={handleSubmit}>Submit</button>

{#if isSubmitted}
  {#if isLoading}
    <p>Hang on, I'm googling it</p>
  {:else if result.length > 0}
    <h1>{submittedName} is a nepo baby!</h1>
    <p>Here are the blue links:</p>
    <ul>
      {#each result as item (item)}
        <li><a target="_blank" href={item}>{extractName(item)}</a></li>
      {/each}
    </ul>
  {:else}
    <h1>{submittedName} is not a nepo baby!</h1>
  {/if}
{/if}
