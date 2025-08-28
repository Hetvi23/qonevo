<script setup>
import { ref } from "vue";
import { call } from "frappe-ui";

const ticketNo = ref("");
const history = ref([]);
const searched = ref(false);
const error = ref("");

function searchTicket() {
  error.value = "";
  history.value = [];
  searched.value = false;

  if (!ticketNo.value) {
    error.value = "Please enter a ticket number.";
    return;
  }

  call(
    "your_custom_app.api.helpdesk.get_ticket_history",
    { ticket_no: ticketNo.value },
    null,
    { show_spinner: true }
  )
    .then((r) => {
      history.value = r.message || [];
      searched.value = true;
    })
    .catch((err) => {
      error.value = err?.message || "Error fetching history.";
    });
}
</script>

<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">🎫 Ticket History Search</h2>

    <div class="flex space-x-2 mb-4">
      <input
        v-model="ticketNo"
        placeholder="Enter Ticket Number"
        @keyup.enter="searchTicket"
        class="border p-2 flex-1"
      />
      <button @click="searchTicket" class="bg-blue-500 text-white px-4 py-2">
        Search
      </button>
    </div>

    <div v-if="error" class="text-red-500 mb-2">{{ error }}</div>

    <table
      v-if="history.length"
      class="table-auto w-full border border-collapse"
    >
      <thead>
        <tr class="bg-gray-100">
          <th class="border px-2 py-1">State</th>
          <th class="border px-2 py-1">Changed By</th>
          <th class="border px-2 py-1">Time</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(h, i) in history" :key="i">
          <td class="border px-2 py-1">{{ h.state }}</td>
          <td class="border px-2 py-1">{{ h.action_by }}</td>
          <td class="border px-2 py-1">{{ h.time }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="!history.length && searched">
      No history found.
    </div>
  </div>
</template>
