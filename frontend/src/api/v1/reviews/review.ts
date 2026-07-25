/**
 * 用例评审模块API接口
 */
import request from '/@/utils/request';

/**
 * 评审状态
 */
export type ReviewStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

/**
 * 评审优先级
 */
export type ReviewPriority = 'low' | 'medium' | 'high' | 'urgent';

/**
 * 评审意见类型
 */
export type CommentType = 'general' | 'suggestion' | 'issue' | 'question';

/**
 * 评审信息
 */
export interface Review {
	id: number;
	project_id: number;
	title: string;
	description?: string;
	status: ReviewStatus;
	priority: ReviewPriority;
	deadline?: string;
	template_id?: number;
	creator_id: number;
	completed_at?: string;
	creation_date: string;
	updation_date: string;
	test_cases?: TestCase[];
	reviewers?: Reviewer[];
}

/**
 * 测试用例
 */
export interface TestCase {
	id: number;
	title: string;
	description?: string;
}

/**
 * 评审人
 */
export interface Reviewer {
	id: number;
	username: string;
	nickname?: string;
	status: string;
	comment?: string;
	reviewed_at?: string;
}

/**
 * 评审意见
 */
export interface ReviewComment {
	id: number;
	review_id: number;
	test_case_id?: number;
	author_id: number;
	author_name: string;
	comment_type: CommentType;
	content: string;
	step_number?: number;
	is_resolved: boolean;
	creation_date: string;
}

/**
 * 评审模板
 */
export interface ReviewTemplate {
	id: number;
	name: string;
	description?: string;
	checklist: Record<string, any>;
	is_active: boolean;
	creator_id: number;
	creation_date: string;
}

/**
 * 评审统计
 */
export interface ReviewStatistics {
	total_reviews: number;
	pending_reviews: number;
	in_progress_reviews: number;
	completed_reviews: number;
	cancelled_reviews: number;
	status_distribution: Record<string, number>;
	priority_distribution: Record<string, number>;
	recent_reviews: Review[];
}

/**
 * 用例评审 API
 */
export function useReviewApi() {
	return {
		getReviewList: (params: {
			page?: number;
			page_size?: number;
			project_id?: number;
			status?: string;
			priority?: string;
		}) =>
			request({
				url: '/v1/Ntesterc_reviews',
				method: 'GET',
				params,
			}),

		getReviewDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${id}`,
				method: 'GET',
			}),

		createReview: (data: {
			project_id: number;
			title: string;
			description?: string;
			priority?: string;
			deadline?: string;
			template_id?: number;
			test_case_ids: number[];
			reviewer_ids: number[];
		}) =>
			request({
				url: '/v1/Ntesterc_reviews',
				method: 'POST',
				data,
			}),

		updateReview: (
			id: number,
			data: {
				title?: string;
				description?: string;
				priority?: string;
				deadline?: string;
				status?: string;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${id}`,
				method: 'PUT',
				data,
			}),

		deleteReview: (id: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${id}`,
				method: 'DELETE',
			}),

		getReviewStatistics: (params: { project_id?: number }) =>
			request({
				url: '/v1/Ntesterc_reviews/statistics',
				method: 'GET',
				params,
			}),

		getMyReviewTasks: (params: {
			page?: number;
			page_size?: number;
			status?: string;
			priority?: string;
			keyword?: string;
		}) =>
			request({
				url: '/v1/Ntesterc_reviews/my-tasks',
				method: 'GET',
				params,
			}),

		startReviewTask: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/start`,
				method: 'POST',
			}),

		getMyReviewResults: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/my-results`,
				method: 'GET',
			}),

		getReviewResults: (
			reviewId: number,
			params?: {
				page?: number;
				page_size?: number;
				result?: string;
				keyword?: string;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/results`,
				method: 'GET',
				params,
			}),

		saveReviewResult: (
			reviewId: number,
			testCaseId: number,
			data: {
				result: string;
				comment?: string;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/testcases/${testCaseId}/review`,
				method: 'POST',
				data,
			}),

		completeReview: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/complete`,
				method: 'POST',
			}),

		getReviewTestCases: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/test-cases`,
				method: 'GET',
			}),

		getReviewReviewers: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/reviewers`,
				method: 'GET',
			}),

		getReviewComments: (
			reviewId: number,
			params?: {
				test_case_id?: number;
				is_resolved?: boolean;
				page?: number;
				page_size?: number;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/comments`,
				method: 'GET',
				params,
			}),

		checkAIReviewAvailability: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/ai-review/availability`,
				method: 'GET',
			}),

		aiReviewSingleTestCase: (reviewId: number, testCaseData: any) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/ai-review/single`,
				method: 'POST',
				data: testCaseData,
			}),

		aiReviewBatchTestCases: (reviewId: number, testCaseIds: number[]) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/ai-review/batch`,
				method: 'POST',
				data: { test_case_ids: testCaseIds },
			}),

		aiPreReviewAllCases: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/my-tasks/${reviewId}/ai-pre-review`,
				method: 'POST',
			}),

		getAIPreReviewSummary: (reviewId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/my-tasks/${reviewId}/ai-pre-review/summary`,
				method: 'GET',
			}),

		assignReviewers: (
			reviewId: number,
			data: {
				reviewer_ids: number[];
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/assign`,
				method: 'POST',
				data,
			}),

		submitReview: (
			reviewId: number,
			data: {
				status: string;
				comment?: string;
				checklist_results?: Record<string, any>;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/submit`,
				method: 'POST',
				data,
			}),

		addReviewComment: (
			reviewId: number,
			data: {
				test_case_id?: number;
				comment_type: string;
				content: string;
				step_number?: number;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/${reviewId}/comments`,
				method: 'POST',
				data,
			}),

		resolveComment: (commentId: number) =>
			request({
				url: `/v1/Ntesterc_reviews/comments/${commentId}/resolve`,
				method: 'POST',
			}),

		getTemplateList: (params: {
			page?: number;
			page_size?: number;
		}) =>
			request({
				url: '/v1/Ntesterc_reviews/templates',
				method: 'GET',
				params,
			}),

		getTemplateDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_reviews/templates/${id}`,
				method: 'GET',
			}),

		createTemplate: (data: {
			name: string;
			description?: string;
			checklist: Record<string, any>;
			project_ids?: number[];
			default_reviewer_ids?: number[];
		}) =>
			request({
				url: '/v1/Ntesterc_reviews/templates',
				method: 'POST',
				data,
			}),

		updateTemplate: (
			id: number,
			data: {
				name?: string;
				description?: string;
				checklist?: Record<string, any>;
				is_active?: boolean;
			}
		) =>
			request({
				url: `/v1/Ntesterc_reviews/templates/${id}`,
				method: 'PUT',
				data,
			}),

		deleteTemplate: (id: number) =>
			request({
				url: `/v1/Ntesterc_reviews/templates/${id}`,
				method: 'DELETE',
			}),
	};
}

const reviewApi = useReviewApi();
export const getReviewList = reviewApi.getReviewList;
export const getReviewDetail = reviewApi.getReviewDetail;
export const createReview = reviewApi.createReview;
export const updateReview = reviewApi.updateReview;
export const deleteReview = reviewApi.deleteReview;
export const getReviewStatistics = reviewApi.getReviewStatistics;
export const getMyReviewTasks = reviewApi.getMyReviewTasks;
export const startReviewTask = reviewApi.startReviewTask;
export const getMyReviewResults = reviewApi.getMyReviewResults;
export const getReviewResults = reviewApi.getReviewResults;
export const saveReviewResult = reviewApi.saveReviewResult;
export const completeReview = reviewApi.completeReview;
export const getReviewTestCases = reviewApi.getReviewTestCases;
export const getReviewReviewers = reviewApi.getReviewReviewers;
export const getReviewComments = reviewApi.getReviewComments;
export const checkAIReviewAvailability = reviewApi.checkAIReviewAvailability;
export const aiReviewSingleTestCase = reviewApi.aiReviewSingleTestCase;
export const aiReviewBatchTestCases = reviewApi.aiReviewBatchTestCases;
export const aiPreReviewAllCases = reviewApi.aiPreReviewAllCases;
export const getAIPreReviewSummary = reviewApi.getAIPreReviewSummary;
export const assignReviewers = reviewApi.assignReviewers;
export const submitReview = reviewApi.submitReview;
export const addReviewComment = reviewApi.addReviewComment;
export const resolveComment = reviewApi.resolveComment;
export const getTemplateList = reviewApi.getTemplateList;
export const getTemplateDetail = reviewApi.getTemplateDetail;
export const createTemplate = reviewApi.createTemplate;
export const updateTemplate = reviewApi.updateTemplate;
export const deleteTemplate = reviewApi.deleteTemplate;
